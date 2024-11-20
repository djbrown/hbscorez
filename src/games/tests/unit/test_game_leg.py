from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from districts.models import District
from games.models import Game, Leg
from leagues.models import League, Season
from teams.models import Team


def create_test_league():
    district = District.objects.create(bhv_id=1)
    season = Season.objects.create(start_year=2018)
    return League.objects.create(name="League 1", abbreviation="L1", bhv_id=1, district=district, season=season)


def create_test_team(number, league) -> Team:
    return Team.objects.create(name=f"Team {number}", short_name=f"T{number}", league=league, bhv_id=number)


def create_test_game(number, league, home_team, guest_team, unscheduled=False) -> Game:
    opening_whistle = timezone.now() + timedelta(weeks=number * 2) if not unscheduled else None
    return Game.objects.create(
        number=number, league=league, opening_whistle=opening_whistle, home_team=home_team, guest_team=guest_team
    )


def assert_games(self, test_data):
    for game, expected_leg in test_data:
        message = f"wrong leg for game '{game.home_team}' vs. '{game.guest_team}'"
        self.assertEqual(expected_leg, game.leg(), msg=message)


class NormalGames(TestCase):

    def test_game_leg(self):
        league = create_test_league()
        team_1 = create_test_team(1, league)
        team_2 = create_test_team(2, league)

        test_data = [
            (create_test_game(0, league=league, home_team=team_1, guest_team=team_2), Leg.FIRST),
            (create_test_game(1, league=league, home_team=team_2, guest_team=team_1), Leg.SECOND),
        ]

        assert_games(self, test_data)

    def test_three_teams(self):
        league = create_test_league()
        team_1 = create_test_team(1, league)
        team_2 = create_test_team(2, league)
        team_3 = create_test_team(3, league)

        test_data = [
            (create_test_game(0, league=league, home_team=team_1, guest_team=team_2), Leg.FIRST),
            (create_test_game(1, league=league, home_team=team_3, guest_team=team_1), Leg.FIRST),
            (create_test_game(2, league=league, home_team=team_2, guest_team=team_1), Leg.SECOND),
            (create_test_game(3, league=league, home_team=team_2, guest_team=team_3), Leg.FIRST),
            (create_test_game(4, league=league, home_team=team_3, guest_team=team_2), Leg.SECOND),
            (create_test_game(5, league=league, home_team=team_1, guest_team=team_3), Leg.SECOND),
        ]

        assert_games(self, test_data)

    def test_four_teams(self):
        league = create_test_league()
        team_1 = create_test_team(1, league)
        team_2 = create_test_team(2, league)
        team_3 = create_test_team(3, league)
        team_4 = create_test_team(4, league)

        test_data = [
            (create_test_game(0, league=league, home_team=team_1, guest_team=team_2), Leg.FIRST),
            (create_test_game(1, league=league, home_team=team_3, guest_team=team_4), Leg.FIRST),
            (create_test_game(2, league=league, home_team=team_2, guest_team=team_1), Leg.SECOND),
            (create_test_game(3, league=league, home_team=team_1, guest_team=team_3), Leg.FIRST),
            (create_test_game(4, league=league, home_team=team_2, guest_team=team_4), Leg.FIRST),
            (create_test_game(5, league=league, home_team=team_1, guest_team=team_4), Leg.FIRST),
            (create_test_game(6, league=league, home_team=team_2, guest_team=team_3), Leg.FIRST),
            (create_test_game(7, league=league, home_team=team_4, guest_team=team_1), Leg.SECOND),
            (create_test_game(8, league=league, home_team=team_4, guest_team=team_3), Leg.SECOND),
            (create_test_game(9, league=league, home_team=team_3, guest_team=team_1), Leg.SECOND),
            (create_test_game(10, league=league, home_team=team_4, guest_team=team_2), Leg.SECOND),
            (create_test_game(11, league=league, home_team=team_3, guest_team=team_2), Leg.SECOND),
        ]

        assert_games(self, test_data)


class UnscheduledGames(TestCase):

    def test_unscheduled_game(self):
        league = create_test_league()
        team_1 = create_test_team(1, league)
        team_2 = create_test_team(2, league)

        test_data = [
            (create_test_game(0, league=league, home_team=team_1, guest_team=team_2, unscheduled=True), Leg.UNKNOWN),
        ]

        assert_games(self, test_data)

    def test_unscheduled_other_games(self):
        league = create_test_league()
        team_1 = create_test_team(1, league)
        team_2 = create_test_team(2, league)

        test_data = [
            (create_test_game(0, league=league, home_team=team_1, guest_team=team_2), Leg.UNKNOWN),
            (create_test_game(1, league=league, home_team=team_2, guest_team=team_1, unscheduled=True), Leg.UNKNOWN),
        ]

        assert_games(self, test_data)


class TripleGames(TestCase):

    def test_game_leg(self):
        league = create_test_league()
        team_1 = create_test_team(1, league)
        team_2 = create_test_team(2, league)

        test_data = [
            (create_test_game(0, league=league, home_team=team_1, guest_team=team_2), Leg.FIRST),
            (create_test_game(1, league=league, home_team=team_1, guest_team=team_2), Leg.BEWTEEN),
            (create_test_game(2, league=league, home_team=team_2, guest_team=team_1), Leg.SECOND),
        ]

        assert_games(self, test_data)

    def test_single_unscheduled(self):
        league = create_test_league()
        team_1 = create_test_team(1, league)
        team_2 = create_test_team(2, league)

        test_data = [
            (create_test_game(0, league=league, home_team=team_1, guest_team=team_2), Leg.UNKNOWN),
            (create_test_game(1, league=league, home_team=team_1, guest_team=team_2, unscheduled=True), Leg.UNKNOWN),
            (create_test_game(2, league=league, home_team=team_2, guest_team=team_1), Leg.UNKNOWN),
        ]

        assert_games(self, test_data)

    def test_three_teams(self):
        league = create_test_league()
        team_1 = create_test_team(1, league)
        team_2 = create_test_team(2, league)
        team_3 = create_test_team(3, league)

        test_data = [
            (create_test_game(0, league=league, home_team=team_1, guest_team=team_2), Leg.FIRST),
            (create_test_game(1, league=league, home_team=team_3, guest_team=team_1), Leg.FIRST),
            (create_test_game(2, league=league, home_team=team_2, guest_team=team_3), Leg.FIRST),
            (create_test_game(3, league=league, home_team=team_2, guest_team=team_1), Leg.BEWTEEN),
            (create_test_game(4, league=league, home_team=team_1, guest_team=team_3), Leg.BEWTEEN),
            (create_test_game(5, league=league, home_team=team_3, guest_team=team_2), Leg.BEWTEEN),
            (create_test_game(6, league=league, home_team=team_1, guest_team=team_2), Leg.SECOND),
            (create_test_game(7, league=league, home_team=team_3, guest_team=team_1), Leg.SECOND),
            (create_test_game(8, league=league, home_team=team_2, guest_team=team_3), Leg.SECOND),
        ]

        assert_games(self, test_data)

    def test_three_teams_single_unscheduled(self):
        league = create_test_league()
        team_1 = create_test_team(1, league)
        team_2 = create_test_team(2, league)
        team_3 = create_test_team(3, league)

        test_data = [
            (create_test_game(0, league=league, home_team=team_1, guest_team=team_2), Leg.UNKNOWN),
            (create_test_game(1, league=league, home_team=team_3, guest_team=team_1), Leg.FIRST),
            (create_test_game(2, league=league, home_team=team_2, guest_team=team_3), Leg.FIRST),
            (create_test_game(3, league=league, home_team=team_2, guest_team=team_1, unscheduled=True), Leg.UNKNOWN),
            (create_test_game(4, league=league, home_team=team_1, guest_team=team_3), Leg.BEWTEEN),
            (create_test_game(5, league=league, home_team=team_3, guest_team=team_2), Leg.BEWTEEN),
            (create_test_game(6, league=league, home_team=team_1, guest_team=team_2), Leg.UNKNOWN),
            (create_test_game(7, league=league, home_team=team_3, guest_team=team_1), Leg.SECOND),
            (create_test_game(8, league=league, home_team=team_2, guest_team=team_3), Leg.SECOND),
        ]

        assert_games(self, test_data)


class QuadrupleGames(TestCase):

    def test_game_leg(self):
        league = create_test_league()
        team_1 = create_test_team(1, league)
        team_2 = create_test_team(2, league)

        test_data = [
            (create_test_game(0, league=league, home_team=team_1, guest_team=team_2), Leg.UNKNOWN),
            (create_test_game(1, league=league, home_team=team_2, guest_team=team_1), Leg.UNKNOWN),
            (create_test_game(2, league=league, home_team=team_1, guest_team=team_2), Leg.UNKNOWN),
            (create_test_game(3, league=league, home_team=team_2, guest_team=team_1), Leg.UNKNOWN),
        ]

        assert_games(self, test_data)
