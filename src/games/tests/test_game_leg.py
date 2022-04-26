from datetime import datetime, timedelta
from typing import Tuple

from django.test import TestCase

from districts.models import District
from games.models import Game, Leg
from leagues.models import League, Season
from teams.models import Team


class NormalGames(TestCase):

    def test_game_leg(self):
        league = create_test_league()
        team_1 = Team.objects.create(name='Team 1', short_name='T1', league=league, bhv_id=1)
        team_2 = Team.objects.create(name='Team 2', short_name='T2', league=league, bhv_id=2)

        earlier_opening_whistle = datetime.now() - timedelta(days=7)
        first_leg_game = Game.objects.create(number=1, league=league, opening_whistle=earlier_opening_whistle,
                                             home_team=team_1, guest_team=team_2)
        second_leg_game = Game.objects.create(number=2, league=league, opening_whistle=datetime.now(),
                                              home_team=team_2, guest_team=team_1)

        self.assertEqual(first_leg_game.leg(), Leg.FIRST)
        self.assertEqual(second_leg_game.leg(), Leg.SECOND)

    def test_three_teams(self):
        league = create_test_league()
        team_1 = Team.objects.create(name='Team 1', short_name='T1', league=league, bhv_id=1)
        team_2 = Team.objects.create(name='Team 2', short_name='T2', league=league, bhv_id=2)
        team_3 = Team.objects.create(name='Team 3', short_name='T3', league=league, bhv_id=3)

        expected = [(team_1, team_2, Leg.FIRST), (team_3, team_1, Leg.FIRST), (team_2, team_1, Leg.SECOND),
                    (team_2, team_3, Leg.FIRST), (team_3, team_2, Leg.SECOND), (team_1, team_3, Leg.SECOND)]

        test_data = [create_test_game(number, league, *vals) for number, vals in enumerate(expected)]

        for game, expected in test_data:
            self.assertEqual(expected, game.leg())

    def test_four_teams(self):
        league = create_test_league()
        team_1 = Team.objects.create(name='Team 1', short_name='T1', league=league, bhv_id=1)
        team_2 = Team.objects.create(name='Team 2', short_name='T2', league=league, bhv_id=2)
        team_3 = Team.objects.create(name='Team 3', short_name='T3', league=league, bhv_id=3)
        team_4 = Team.objects.create(name='Team 4', short_name='T4', league=league, bhv_id=4)

        expected = [(team_1, team_2, Leg.FIRST), (team_3, team_4, Leg.FIRST), (team_2, team_1, Leg.SECOND),
                    (team_1, team_3, Leg.FIRST), (team_2, team_4, Leg.FIRST), (team_1, team_4, Leg.FIRST),
                    (team_2, team_3, Leg.FIRST), (team_4, team_1, Leg.SECOND), (team_4, team_3, Leg.SECOND),
                    (team_3, team_1, Leg.SECOND), (team_4, team_2, Leg.SECOND), (team_3, team_2, Leg.SECOND),
                    ]

        test_data = [create_test_game(number, league, *vals) for number, vals in enumerate(expected)]

        for game, expected in test_data:
            self.assertEqual(expected, game.leg())


def create_test_game(number, league, home_team, guest_team, expected_leg: Leg, unscheduled=False) -> Tuple[Game, Leg]:
    opening_whistle = datetime.now() + timedelta(weeks=number * 2) if not unscheduled else None
    game = Game.objects.create(number=number, league=league, opening_whistle=opening_whistle,
                               home_team=home_team, guest_team=guest_team)
    return game, expected_leg


def create_test_league():
    district = District.objects.create(bhv_id=1)
    season = Season.objects.create(start_year=2018)
    return League.objects.create(name='League 1', abbreviation='L1', bhv_id=1, district=district, season=season)


class UnscheduledGames(TestCase):

    def test_unscheduled_game(self):
        league = create_test_league()
        team_1 = Team.objects.create(name='Team 1', short_name='T1', league=league, bhv_id=1)
        team_2 = Team.objects.create(name='Team 2', short_name='T2', league=league, bhv_id=2)

        game = Game.objects.create(number=1, league=league, opening_whistle=None, home_team=team_1, guest_team=team_2)

        self.assertEqual(game.leg(), Leg.UNKNOWN)

    def test_unscheduled_other_games(self):
        league = create_test_league()
        team_1 = Team.objects.create(name='Team 1', short_name='T1', league=league, bhv_id=1)
        team_2 = Team.objects.create(name='Team 2', short_name='T2', league=league, bhv_id=2)

        game = Game.objects.create(number=1, league=league, opening_whistle=datetime.now(),
                                   home_team=team_1, guest_team=team_2)

        Game.objects.create(number=2, league=league, opening_whistle=None, home_team=team_2, guest_team=team_1)
        self.assertEqual(game.leg(), Leg.UNKNOWN)


class TripleGames(TestCase):

    def test_game_leg(self):
        league = create_test_league()
        team_1 = Team.objects.create(name='Team 1', short_name='T1', league=league, bhv_id=1)
        team_2 = Team.objects.create(name='Team 2', short_name='T2', league=league, bhv_id=2)

        first = Game.objects.create(number=1, league=league, home_team=team_1, guest_team=team_2,
                                    opening_whistle=datetime.now() - timedelta(days=7))
        between = Game.objects.create(number=2, league=league, home_team=team_1, guest_team=team_2,
                                      opening_whistle=datetime.now() - timedelta(days=5))
        second = Game.objects.create(number=3, league=league, home_team=team_2,
                                     guest_team=team_1, opening_whistle=datetime.now())

        self.assertEqual(first.leg(), Leg.FIRST)
        self.assertEqual(between.leg(), Leg.BEWTEEN)
        self.assertEqual(second.leg(), Leg.SECOND)

    def test_single_unscheduled(self):
        league = create_test_league()
        team_1 = Team.objects.create(name='Team 1', short_name='T1', league=league, bhv_id=1)
        team_2 = Team.objects.create(name='Team 2', short_name='T2', league=league, bhv_id=2)

        first = Game.objects.create(number=1, league=league, home_team=team_1, guest_team=team_2,
                                    opening_whistle=datetime.now() - timedelta(days=7))
        unsheduled = Game.objects.create(number=2, league=league, home_team=team_1, guest_team=team_2)
        second = Game.objects.create(number=3, league=league, home_team=team_2,
                                     guest_team=team_1, opening_whistle=datetime.now())

        self.assertEqual(first.leg(), Leg.UNKNOWN)
        self.assertEqual(unsheduled.leg(), Leg.UNKNOWN)
        self.assertEqual(second.leg(), Leg.UNKNOWN)

    def test_three_teams(self):
        league = create_test_league()
        team_1 = Team.objects.create(name='Team 1', short_name='T1', league=league, bhv_id=1)
        team_2 = Team.objects.create(name='Team 2', short_name='T2', league=league, bhv_id=2)
        team_3 = Team.objects.create(name='Team 3', short_name='T3', league=league, bhv_id=3)

        expected = [(team_1, team_2, Leg.FIRST), (team_3, team_1, Leg.FIRST), (team_2, team_3, Leg.FIRST),
                    (team_2, team_1, Leg.BEWTEEN), (team_1, team_3, Leg.BEWTEEN), (team_3, team_2, Leg.BEWTEEN),
                    (team_1, team_2, Leg.SECOND), (team_3, team_1, Leg.SECOND), (team_2, team_3, Leg.SECOND)]

        test_data = [create_test_game(number, league, *vals) for number, vals in enumerate(expected)]

        for game, expected in test_data:
            self.assertEqual(expected, game.leg())

    def test_three_teams_single_unscheduled(self):
        league = create_test_league()
        team_1 = Team.objects.create(name='Team 1', short_name='T1', league=league, bhv_id=1)
        team_2 = Team.objects.create(name='Team 2', short_name='T2', league=league, bhv_id=2)
        team_3 = Team.objects.create(name='Team 3', short_name='T3', league=league, bhv_id=3)

        expected = [(team_1, team_2, Leg.UNKNOWN), (team_3, team_1, Leg.FIRST), (team_2, team_3, Leg.FIRST),
                    (team_2, team_1, Leg.UNKNOWN, True), (team_1, team_3, Leg.BEWTEEN), (team_3, team_2, Leg.BEWTEEN),
                    (team_1, team_2, Leg.UNKNOWN), (team_3, team_1, Leg.SECOND), (team_2, team_3, Leg.SECOND)]

        test_data = [create_test_game(number, league, *vals) for number, vals in enumerate(expected)]

        for game, expected in test_data:
            self.assertEqual(expected, game.leg(), msg=f"wrong leg for game '{game.home_team}' vs. '{game.guest_team}'")


class QuadrupleGames(TestCase):

    def test_game_leg(self):
        league = create_test_league()
        team_1 = Team.objects.create(name='Team 1', short_name='T1', league=league, bhv_id=1)
        team_2 = Team.objects.create(name='Team 2', short_name='T2', league=league, bhv_id=2)

        first = Game.objects.create(number=1, league=league, home_team=team_1, guest_team=team_2,
                                    opening_whistle=datetime.now() - timedelta(days=7))
        second = Game.objects.create(number=2, league=league, home_team=team_2, guest_team=team_1,
                                     opening_whistle=datetime.now() - timedelta(days=5))
        third = Game.objects.create(number=3, league=league, home_team=team_1, guest_team=team_2,
                                    opening_whistle=datetime.now() - timedelta(days=3))
        fourth = Game.objects.create(number=4, league=league, home_team=team_2, guest_team=team_1,
                                     opening_whistle=datetime.now())

        self.assertEqual(first.leg(), Leg.UNKNOWN)
        self.assertEqual(second.leg(), Leg.UNKNOWN)
        self.assertEqual(third.leg(), Leg.UNKNOWN)
        self.assertEqual(fourth.leg(), Leg.UNKNOWN)
