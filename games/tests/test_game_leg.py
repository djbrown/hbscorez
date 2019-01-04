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

        self.assertEqual(first_leg_game.leg(), Leg.FIRST_LEG)
        self.assertEqual(second_leg_game.leg(), Leg.SECOND_LEG)

    def test_three_teams(self):
        league = create_test_league()
        team_1 = Team.objects.create(name='Team 1', short_name='T1', league=league, bhv_id=1)
        team_2 = Team.objects.create(name='Team 2', short_name='T2', league=league, bhv_id=2)
        team_3 = Team.objects.create(name='Team 3', short_name='T3', league=league, bhv_id=3)

        expected = [(team_1, team_2, Leg.FIRST_LEG), (team_3, team_1, Leg.FIRST_LEG), (team_2, team_1, Leg.SECOND_LEG),
                    (team_2, team_3, Leg.FIRST_LEG), (team_3, team_2, Leg.SECOND_LEG), (team_1, team_3, Leg.SECOND_LEG)]

        test_data = [create_test_game(number, league, *vals) for number, vals in enumerate(expected)]

        for game, expected in test_data:
            self.assertEqual(expected, game.leg())

    def test_four_teams(self):
        league = create_test_league()
        team_1 = Team.objects.create(name='Team 1', short_name='T1', league=league, bhv_id=1)
        team_2 = Team.objects.create(name='Team 2', short_name='T2', league=league, bhv_id=2)
        team_3 = Team.objects.create(name='Team 3', short_name='T3', league=league, bhv_id=3)
        team_4 = Team.objects.create(name='Team 4', short_name='T4', league=league, bhv_id=4)

        expected = [(team_1, team_2, Leg.FIRST_LEG), (team_3, team_4, Leg.FIRST_LEG), (team_2, team_1, Leg.SECOND_LEG),
                    (team_1, team_3, Leg.FIRST_LEG), (team_2, team_4, Leg.FIRST_LEG), (team_1, team_4, Leg.FIRST_LEG),
                    (team_2, team_3, Leg.FIRST_LEG), (team_4, team_1, Leg.SECOND_LEG), (team_4, team_3, Leg.SECOND_LEG),
                    (team_3, team_1, Leg.SECOND_LEG), (team_4, team_2, Leg.SECOND_LEG), (team_3, team_2, Leg.SECOND_LEG)
                    ]

        test_data = [create_test_game(number, league, *vals) for number, vals in enumerate(expected)]

        for game, expected in test_data:
            self.assertEqual(expected, game.leg())


def create_test_game(number, league, home_team, guest_team, expected_leg: Leg) -> Tuple[Game, Leg]:
    opening_whistle = datetime.now() + timedelta(weeks=number * 2)
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

    def test_unscheduled_other_game(self):
        league = create_test_league()
        team_1 = Team.objects.create(name='Team 1', short_name='T1', league=league, bhv_id=1)
        team_2 = Team.objects.create(name='Team 2', short_name='T2', league=league, bhv_id=2)

        game = Game.objects.create(number=1, league=league, opening_whistle=datetime.now(),
                                   home_team=team_1, guest_team=team_2)

        Game.objects.create(number=2, league=league, opening_whistle=None, home_team=team_2, guest_team=team_1)
        self.assertEqual(game.leg(), Leg.UNKNOWN)
