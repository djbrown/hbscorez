import locale
import re
import typing
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path

from django.conf import settings
from django.db import models
from django.urls import reverse


class Association(models.Model):
    name = models.TextField(unique=True)
    abbreviation = models.TextField()
    bhv_id = models.IntegerField(unique=True)

    def __str__(self):
        return 'Association: {} ({})'.format(self.bhv_id, self.abbreviation)

    def get_absolute_url(self):
        return reverse('association', kwargs={'bhv_id': self.bhv_id})

    def source_url(self):
        return 'https://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID={}'.format(self.bhv_id)


class District(models.Model):
    name = models.TextField(unique=True)
    associations = models.ManyToManyField(Association)
    bhv_id = models.IntegerField(unique=True)

    def __str__(self):
        return 'District: {} ({})'.format(self.bhv_id, self.name)

    def get_absolute_url(self):
        return reverse('district', kwargs={'bhv_id': self.bhv_id})

    def source_url(self):
        return 'https://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID={}&orgID={}'.format(
            self.associations.all()[0].bhv_id,
            self.bhv_id)


class League(models.Model):
    name = models.TextField()
    abbreviation = models.TextField()
    district = models.ForeignKey(District)
    bhv_id = models.IntegerField(unique=True)

    class Meta:
        unique_together = (('name', 'district'), ('abbreviation', 'district'))

    def __str__(self):
        return 'League: {} ({})'.format(self.bhv_id, self.name)

    def get_absolute_url(self):
        return reverse('league', kwargs={'bhv_id': self.bhv_id})

    def players_url(self):
        return reverse('league_players', kwargs={'bhv_id': self.bhv_id})

    def source_url(self):
        return 'https://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID={}&score={}&all=1'.format(
            self.district.associations.all()[0].bhv_id, self.bhv_id)

    @staticmethod
    def is_youth_league(abbreviation, name):
        return abbreviation[:1] in ['m', 'w', 'g', 'u'] \
               or re.search('MJ', name) \
               or re.search('WJ', name) \
               or re.search('Jugend', name) \
               or re.search('Mini', name)


class Team(models.Model):
    name = models.TextField()
    short_name = models.TextField()
    league = models.ForeignKey(League)
    bhv_id = models.IntegerField(unique=True)
    # logo = models.ImageField(upload_to=os.path.join(settings.MEDIA_ROOT, 'club-logos'))

    class Meta:
        unique_together = (('name', 'league'), ('short_name', 'league'))

    def __str__(self):
        return '{} ({})'.format(self.short_name, self.bhv_id)

    def get_absolute_url(self):
        return reverse('team', kwargs={'bhv_id': self.bhv_id, })

    def source_url(self):
        return 'https://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID={}&score={}&teamID={}'.format(
            self.league.district.associations.all()[0].bhv_id, self.league.bhv_id, self.bhv_id)


class Player(models.Model):
    name = models.TextField()
    team = models.ForeignKey(Team)

    def __str__(self):
        return '{} ({})'.format(self.name, self.team.short_name)

    def get_absolute_url(self):
        return reverse('player', kwargs={'pk': self.pk})


class SportsHall(models.Model):
    number = models.IntegerField(unique=True)
    name = models.TextField()
    address = models.TextField()
    phone_number = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return "{} {}".format(self.number, self.name)


class GameOutcome(Enum):
    HOME_WIN = auto()
    AWAY_WIN = auto()
    TIE = auto()


class TeamOutCome(Enum):
    WIN = auto()
    LOSS = auto()
    TIE = auto()


class Game(models.Model):
    number = models.IntegerField(unique=True)
    league = models.ForeignKey(League)
    opening_whistle = models.DateTimeField()
    sports_hall = models.ForeignKey(SportsHall)
    home_team = models.ForeignKey(Team, related_name='home_team')
    guest_team = models.ForeignKey(Team, related_name='guest_team')
    home_goals = models.IntegerField(blank=True, null=True)
    guest_goals = models.IntegerField(blank=True, null=True)
    report_number = models.IntegerField(unique=True, blank=True, null=True)

    def __str__(self):
        return '{}: {} vs. {}'.format(self.number, self.home_team.short_name, self.guest_team.short_name)

    def report_url(self):
        return 'https://spo.handball4all.de/misc/sboPublicReports.php?sGID={}'.format(self.report_number)

    def report_path(self):
        return Path(settings.REPORTS_PATH).joinpath(str(self.report_number) + '.pdf')

    def opponent_of(self, team):
        if team == self.home_team:
            return self.guest_team
        elif team == self.guest_team:
            return self.home_team

    def other_game(self):
        games = Game.objects.filter(home_team__in=(self.home_team, self.guest_team),
                                    guest_team__in=(self.home_team, self.guest_team))
        assert len(games) == 2
        assert self in games
        return games.get(~models.Q(number=self.number))

    def is_first_leg(self):
        other_game = self.other_game()
        return self.opening_whistle < other_game.opening_whistle

    def outcome(self) -> GameOutcome:
        if self.home_goals > self.guest_goals:
            return GameOutcome.HOME_WIN
        if self.home_goals < self.guest_goals:
            return GameOutcome.AWAY_WIN
        if self.home_goals == self.guest_goals:
            return GameOutcome.TIE

    def outcome_for(self, team) -> TeamOutCome:
        if self.outcome() == GameOutcome.TIE:
            return TeamOutCome.TIE
        if team == self.home_team and self.outcome() == GameOutcome.HOME_WIN \
                or team == self.guest_team and self.outcome() == GameOutcome.AWAY_WIN:
            return TeamOutCome.WIN
        if team == self.home_team and self.outcome() == GameOutcome.AWAY_WIN \
                or team == self.guest_team and self.outcome() == GameOutcome.HOME_WIN:
            return TeamOutCome.LOSS

    @staticmethod
    def parse_opening_whistle(text) -> datetime:
        locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
        return datetime.strptime(text, '%a, %d.%m.%y, %H:%Mh')


class Score(models.Model):
    player = models.ForeignKey(Player)
    player_number = models.PositiveIntegerField()
    game = models.ForeignKey(Game)
    goals = models.PositiveIntegerField()
    penalty_goals = models.PositiveIntegerField()
    penalty_tries = models.PositiveIntegerField()
    warning_time = models.DurationField(blank=True, null=True)
    first_suspension_time = models.DurationField(blank=True, null=True)
    second_suspension_time = models.DurationField(blank=True, null=True)
    third_suspension_time = models.DurationField(blank=True, null=True)
    disqualification_time = models.DurationField(blank=True, null=True)
    # report_time = models.DurationField(blank=True, null=True)
    team_suspension_time = models.DurationField(blank=True, null=True)

    class Meta:
        unique_together = ('player', 'game')

    def __str__(self):
        return '{} - {} ({})'.format(self.game, self.player, self.player_number)

    @staticmethod
    def parse_game_time(text: str) -> typing.Optional[timedelta]:
        if not text:
            return None

        minutes, seconds = text.split(':')
        return timedelta(minutes=int(minutes), seconds=int(seconds))
