import typing
from enum import Enum, auto
from pathlib import Path

import faker
from django.conf import settings
from django.core import validators
from django.db import models
from django.urls import reverse

from base import source_url


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
        return source_url.association_source_url(self.bhv_id)


class District(models.Model):
    name = models.TextField(unique=True)
    associations = models.ManyToManyField(Association)
    bhv_id = models.IntegerField(unique=True)

    def __str__(self):
        return '{} {}'.format(self.bhv_id, self.name)

    def get_absolute_url(self):
        return reverse('district', kwargs={'bhv_id': self.bhv_id})

    def source_url(self):
        return source_url.district_source_url(self.bhv_id)


class Season(models.Model):
    start_year = models.PositiveIntegerField(unique=True, validators=[
        validators.MinValueValidator(1990),
        validators.MaxValueValidator(2050)])

    def __str__(self):
        return '{}/{}'.format(self.start_year, self.start_year + 1)


class League(models.Model):
    name = models.TextField()
    abbreviation = models.TextField()
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    bhv_id = models.IntegerField(unique=True)

    class Meta:
        unique_together = (('name', 'district'), ('abbreviation', 'district'))

    def __str__(self):
        return '{} {}'.format(self.name, self.season)

    def get_absolute_url(self):
        return reverse('league_overview', kwargs={'bhv_id': self.bhv_id})

    def source_url(self):
        return source_url.league_source_url(self.bhv_id)


class Team(models.Model):
    name = models.TextField()
    short_name = models.TextField()
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    bhv_id = models.IntegerField(unique=True)

    # logo = models.ImageField(upload_to=os.path.join(settings.MEDIA_ROOT, 'club-logos'))

    class Meta:
        unique_together = (('name', 'league'), ('short_name', 'league'))

    def __str__(self):
        return '{} {}'.format(self.bhv_id, self.short_name)

    def get_absolute_url(self):
        return reverse('team_overview', kwargs={'bhv_id': self.bhv_id, })

    def source_url(self):
        return source_url.team_source_url(self.league.bhv_id, self.bhv_id)


class Player(models.Model):
    name = models.TextField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.name, self.team.short_name)

    def get_absolute_url(self):
        return reverse('player', kwargs={'pk': self.pk})

    def fake_name(self):
        factory = faker.Faker('de_DE')
        factory.seed(self.pk)
        return factory.name()


class SportsHall(models.Model):
    number = models.IntegerField(unique=True)
    name = models.TextField()
    address = models.TextField()
    phone_number = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(blank=True, null=True, max_digits=9, decimal_places=6)
    longitude = models.DecimalField(blank=True, null=True, max_digits=9, decimal_places=6)
    bhv_id = models.IntegerField(unique=True)

    def __str__(self):
        return "{} {}".format(self.number, self.name)

    def source_url(self):
        return source_url.sports_hall_source_url(self.bhv_id)


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
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    opening_whistle = models.DateTimeField(blank=True, null=True)
    sports_hall = models.ForeignKey(SportsHall, on_delete=models.CASCADE, blank=True, null=True)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_team')
    guest_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='guest_team')
    home_goals = models.IntegerField(blank=True, null=True)
    guest_goals = models.IntegerField(blank=True, null=True)
    report_number = models.IntegerField(unique=True, blank=True, null=True)
    forfeiting_team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True,
                                        related_name='forfeiting_team')

    def __str__(self):
        return '{} {} vs. {}'.format(self.number, self.home_team.short_name, self.guest_team.short_name)

    def report_url(self):
        if self.report_number is None:
            return None
        return source_url.report_source_url(self.report_number)

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


class Score(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    player_number = models.IntegerField(blank=True, null=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
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
