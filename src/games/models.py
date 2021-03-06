from enum import Enum, auto

from django.conf import settings
from django.db import models

from leagues.models import League
from sports_halls.models import SportsHall
from teams.models import Team


class GameOutcome(Enum):
    HOME_WIN = auto()
    AWAY_WIN = auto()
    TIE = auto()
    OPEN = auto()


class TeamOutcome(Enum):
    WIN = auto()
    LOSS = auto()
    TIE = auto()
    OPEN = auto()


class Leg(Enum):
    FIRST = auto()
    BEWTEEN = auto()
    SECOND = auto()
    UNKNOWN = auto()


class Game(models.Model):
    number = models.IntegerField()
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
    spectators = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('number', 'league')

    def __str__(self):
        return '{} {} {} vs. {}'.format(self.number, self.league, self.home_team.short_name, self.guest_team.short_name)

    @staticmethod
    def build_report_source_url(report_number):
        return settings.ROOT_SOURCE_URL + 'misc/sboPublicReports.php?sGID={}'.format(report_number)

    def report_source_url(self):
        if self.report_number is None:
            return None
        return self.build_report_source_url(self.report_number)

    def opponent_of(self, team):
        if team == self.home_team:
            return self.guest_team
        if team == self.guest_team:
            return self.home_team
        raise ValueError('neither home or guest is team: {}'.format(team))

    def other_games(self):
        return Game.objects.filter(~models.Q(number=self.number),
                                   home_team__in=(self.home_team, self.guest_team),
                                   guest_team__in=(self.home_team, self.guest_team))

    def leg(self) -> Leg:
        if self.opening_whistle is None:
            return Leg.UNKNOWN

        other_games = self.other_games()
        if not other_games \
                or list(filter(lambda g: g.opening_whistle is None, other_games)):
            return Leg.UNKNOWN

        if len(other_games) == 1:
            first_leg = self.opening_whistle < other_games[0].opening_whistle
            return Leg.FIRST if first_leg else Leg.SECOND

        if len(other_games) == 2:
            if self.opening_whistle < other_games[0].opening_whistle \
                    and self.opening_whistle < other_games[1].opening_whistle:
                return Leg.FIRST
            if self.opening_whistle > other_games[0].opening_whistle \
                    and self.opening_whistle > other_games[1].opening_whistle:
                return Leg.SECOND

            return Leg.BEWTEEN

        raise RuntimeError('More than 2 other games found on {}'.format(self))

    def leg_title(self) -> str:
        mapping = {
            Leg.FIRST: "Hinspiel",
            Leg.BEWTEEN: "Zwischenspiel",
            Leg.SECOND: "Rückspiel",
            Leg.UNKNOWN: "Spiel",
        }
        return mapping[self.leg()]

    def outcome(self) -> GameOutcome:
        if self.home_goals is None and self.guest_goals is None:
            return GameOutcome.OPEN
        if self.home_goals > self.guest_goals \
                or self.forfeiting_team == self.guest_team:
            return GameOutcome.HOME_WIN
        if self.home_goals < self.guest_goals \
                or self.forfeiting_team == self.home_team:
            return GameOutcome.AWAY_WIN
        if self.home_goals == self.guest_goals:
            return GameOutcome.TIE
        raise ValueError('no matching outcome')

    def outcome_for(self, team) -> TeamOutcome:
        if self.outcome() == GameOutcome.OPEN:
            return TeamOutcome.OPEN
        if self.outcome() == GameOutcome.TIE:
            return TeamOutcome.TIE
        if team == self.home_team and self.outcome() == GameOutcome.HOME_WIN \
                or team == self.guest_team and self.outcome() == GameOutcome.AWAY_WIN:
            return TeamOutcome.WIN
        if team == self.home_team and self.outcome() == GameOutcome.AWAY_WIN \
                or team == self.guest_team and self.outcome() == GameOutcome.HOME_WIN:
            return TeamOutcome.LOSS
        raise ValueError('no matching outcome for team: {}'.format(team))

    def goals_of(self, team):
        if team == self.home_team:
            return self.home_goals
        if team == self.guest_team:
            return self.guest_goals
        return 0
