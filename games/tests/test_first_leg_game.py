from datetime import datetime, timedelta
from typing import Tuple

from django.test import TestCase

from districts.models import District
from games.models import Game
from leagues.models import League, Season
from teams.models import Team


class FirstLegGameTest(TestCase):

    def test_first_leg_game_returns_true(self):
        league = create_test_league()
        team_1 = Team.objects.create(name='Team 1', short_name='T1', league=league, bhv_id=1)
        team_2 = Team.objects.create(name='Team 2', short_name='T2', league=league, bhv_id=2)

        earlier_opening_whistle = datetime.now() - timedelta(days=7)
        first_leg_game = Game.objects.create(number=1, league=league,
                                             opening_whistle=earlier_opening_whistle,
                                             home_team=team_1, guest_team=team_2, home_goals=0, guest_goals=0,
                                             report_number=1)
        Game.objects.create(number=2, league=league, opening_whistle=datetime.now(), home_team=team_2,
                            guest_team=team_1, home_goals=0, guest_goals=0, report_number=2)

        actual = first_leg_game.is_first_leg()

        expected = True

        self.assertEqual(expected, actual)

    def test_second_leg_game_returns_false(self):
        league = create_test_league()
        team_1 = Team.objects.create(name='Team 1', short_name='T1', league=league, bhv_id=1)
        team_2 = Team.objects.create(name='Team 2', short_name='T2', league=league, bhv_id=2)

        Game.objects.create(number=1, league=league, opening_whistle=datetime.now(), home_team=team_1,
                            guest_team=team_2, home_goals=0, guest_goals=0, report_number=1)
        later_opening_whistle = datetime.now() + timedelta(days=7)
        second_leg_game = Game.objects.create(number=2, league=league,
                                              opening_whistle=later_opening_whistle,
                                              home_team=team_1, guest_team=team_2, home_goals=0, guest_goals=0,
                                              report_number=2)

        actual = second_leg_game.is_first_leg()

        expected = False

        self.assertEqual(expected, actual)

    def test_three_teams(self):
        league = create_test_league()
        team_1 = Team.objects.create(name='Team 1', short_name='T1', league=league, bhv_id=1)
        team_2 = Team.objects.create(name='Team 2', short_name='T2', league=league, bhv_id=2)
        team_3 = Team.objects.create(name='Team 3', short_name='T3', league=league, bhv_id=3)

        expected = [(team_1, team_2, True), (team_3, team_1, True), (team_2, team_1, False),
                    (team_2, team_3, True), (team_3, team_2, False), (team_1, team_3, False)]

        test_data = [create_test_game(number, league, *vals) for number, vals in enumerate(expected)]

        for game, expected in test_data:
            self.assertEqual(expected, game.is_first_leg())

    def test_four_teams(self):
        league = create_test_league()
        team_1 = Team.objects.create(name='Team 1', short_name='T1', league=league, bhv_id=1)
        team_2 = Team.objects.create(name='Team 2', short_name='T2', league=league, bhv_id=2)
        team_3 = Team.objects.create(name='Team 3', short_name='T3', league=league, bhv_id=3)
        team_4 = Team.objects.create(name='Team 4', short_name='T4', league=league, bhv_id=4)

        expected = [(team_1, team_2, True), (team_3, team_4, True), (team_2, team_1, False), (team_1, team_3, True),
                    (team_2, team_4, True), (team_1, team_4, True), (team_2, team_3, True), (team_4, team_1, False),
                    (team_4, team_3, False), (team_3, team_1, False), (team_4, team_2, False), (team_3, team_2, False)]

        test_data = [create_test_game(number, league, *vals) for number, vals in enumerate(expected)]

        for game, expected in test_data:
            self.assertEqual(expected, game.is_first_leg())


def create_test_game(number, league, home_team, guest_team, should_be_first_leg) -> Tuple[Game, bool]:
    opening_whistle = datetime.now() + timedelta(weeks=number * 2)
    game = Game.objects.create(number=number, league=league, opening_whistle=opening_whistle,
                               home_team=home_team, guest_team=guest_team, home_goals=0, guest_goals=0,
                               report_number=number)
    return game, should_be_first_leg


def create_test_league():
    district = District.objects.create(bhv_id=1)
    season = Season.objects.create(start_year=2018)
    league = League.objects.create(
        name='League 1', abbreviation='L1', bhv_id=1, district=district, season=season)
    return league
