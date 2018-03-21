import locale
import re
import typing
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

from django.conf import settings
from django.db import models
from django.urls import reverse


class Value(Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"


class Env(models.Model):
    name = models.TextField(unique=True)
    value = models.TextField()

    def set_value(self, value: Value):
        self.value = value.value
        self.save()


class Association(models.Model):
    name = models.TextField(unique=True)
    abbreviation = models.TextField()
    bhv_id = models.IntegerField(unique=True)

    def __str__(self):
        return '{} {}'.format(self.bhv_id, self.abbreviation)

    def get_absolute_url(self):
        return reverse('association', kwargs={'bhv_id': self.bhv_id})

    def source_url(self):
        return 'https://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID={}'.format(self.bhv_id)


class District(models.Model):
    name = models.TextField(unique=True)
    associations = models.ManyToManyField(Association)
    bhv_id = models.IntegerField(unique=True)

    def __str__(self):
        return '{} {}'.format(self.bhv_id, self.name)

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
        return '{} {}'.format(self.bhv_id, self.name)

    def get_absolute_url(self):
        return reverse('league_overview', kwargs={'bhv_id': self.bhv_id})

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
        return '{} {}'.format(self.bhv_id, self.short_name)

    def get_absolute_url(self):
        return reverse('team_overview', kwargs={'bhv_id': self.bhv_id, })

    def source_url(self):
        return 'https://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID={}&score={}&teamID={}'.format(
            self.league.district.associations.all()[0].bhv_id, self.league.bhv_id, self.bhv_id)


class Player(models.Model):
    name = models.TextField()
    team = models.ForeignKey(Team)

    def __str__(self):
        return '{} {}'.format(self.name, self.team.short_name)

    def get_absolute_url(self):
        return reverse('player', kwargs={'pk': self.pk})


class SportsHall(models.Model):
    number = models.IntegerField(unique=True)
    name = models.TextField()
    address = models.TextField()
    phone_number = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    bhv_id = models.IntegerField(unique=True)

    def __str__(self):
        return "{} {}".format(self.number, self.name)

    @staticmethod
    def parse_bhv_id(link):
        href = link.get('href')
        query = urlsplit(href).query
        return int(parse_qs(query)['gymID'][0])


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
    opening_whistle = models.DateTimeField(blank=True, null=True)
    sports_hall = models.ForeignKey(SportsHall)
    home_team = models.ForeignKey(Team, related_name='home_team')
    guest_team = models.ForeignKey(Team, related_name='guest_team')
    home_goals = models.IntegerField(blank=True, null=True)
    guest_goals = models.IntegerField(blank=True, null=True)
    report_number = models.IntegerField(unique=True, blank=True, null=True)
    forfeiting_team = models.ForeignKey(Team, blank=True, null=True, related_name='forfeiting_team')

    def __str__(self):
        return '{} {} vs. {}'.format(self.number, self.home_team.short_name, self.guest_team.short_name)

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
        return games.get(~models.Q(number=self.number))

    def is_first_leg(self):
        other_game = self.other_game()
        if not other_game:
            return True
        return self.opening_whistle < other_game.opening_whistle

    def outcome(self) -> typing.Optional[GameOutcome]:
        if self.home_goals is None and self.guest_goals is None:
            return None
        if self.home_goals > self.guest_goals \
                or self.forfeiting_team == self.guest_team:
            return GameOutcome.HOME_WIN
        if self.home_goals < self.guest_goals \
                or self.forfeiting_team == self.home_team:
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

    def goals_of(self, team):
        if team == self.home_team:
            return self.home_goals
        if team == self.guest_team:
            return self.guest_goals
        return 0

    @staticmethod
    def parse_opening_whistle(text) -> typing.Optional[datetime]:
        if not text.strip():
            return None
        locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
        return datetime.strptime(text, '%a, %d.%m.%y, %H:%Mh')

    @staticmethod
    def parse_report_number(cell):
        if len(cell) == 1 and cell[0].text == 'PI':
            href = cell[0].get('href')
            query = urlsplit(href).query
            return int(parse_qs(query)['sGID'][0])
        else:
            return None

    @staticmethod
    def parse_forfeiting_team(cell, home_team, guest_team):
        if cell.text == " (2:0)":
            return guest_team
        if cell.text == " (0:2)":
            return home_team


class Score(models.Model):
    player = models.ForeignKey(Player)
    player_number = models.IntegerField()
    game = models.ForeignKey(Game)
    goals = models.IntegerField()
    penalty_goals = models.IntegerField()
    penalty_tries = models.IntegerField()
    warning_time = models.DurationField(blank=True, null=True)
    first_suspension_time = models.DurationField(blank=True, null=True)
    second_suspension_time = models.DurationField(blank=True, null=True)
    third_suspension_time = models.DurationField(blank=True, null=True)
    disqualification_time = models.DurationField(blank=True, null=True)
    report_time = models.DurationField(blank=True, null=True)
    team_suspension_time = models.DurationField(blank=True, null=True)

    class Meta:
        unique_together = ('player', 'game')

    def __str__(self):
        return '{} {} ({})'.format(self.game.number, self.player.name, self.player_number)

    @staticmethod
    def parse_game_time(text: str) -> typing.Optional[timedelta]:
        if not text:
            return None

        minutes, seconds = text.split(':')
        return timedelta(minutes=int(minutes), seconds=int(seconds))
