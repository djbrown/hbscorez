import datetime

from base.tests.base import IntegrationTestCase
from games.models import Game
from leagues.models import League, Season
from leagues.tests.integration import test_setup_league


class ImportGamesTest(IntegrationTestCase):

    def test__import_games__specific_game(self):
        self.assert_command('setup', '-a', 35, '-d', 35, '-s', 2017, '-l', 26777)
        league = self.assert_objects(League)

        self.assert_command('import_games', '-g', 210226)
        game = self.assert_objects(Game)

        self.assertEqual(game.number, 210226)
        self.assertEqual(game.opening_whistle, datetime.datetime(2017, 10, 7, 19, 45))
        self.assertEqual(game.home_team.short_name, 'TSVG Malsch')
        self.assertEqual(game.guest_team.short_name, 'HSG Dittig/TBB')
        self.assertEqual(game.home_goals, 24)
        self.assertEqual(game.guest_goals, 22)
        self.assertEqual(game.report_number, 490394)
        self.assertEqual(game.sports_hall.number, 22010)
        self.assertEqual(game.league, league)

    def test__import_games__m_vl(self):
        self.assert_command('setup', '-a', 35, '-d', 35, '-s', 2017, '-l', 26777)
        self.assert_objects(League)

        self.assert_command('import_games')
        self.assert_objects(Game, 182)

    def test__import_games__missing_district(self):
        self.assert_command('import_games', '-a', 35, '-d', 0)
        self.assert_objects(Game, 0)

    def test__import_games__m_vl__multiseason(self):
        self.assert_command('setup', '-a', 35, '-d', 35, '-s', 2017, 2018, '-l', 26777, 34606)
        self.assert_objects(Season, count=2)
        leagues = self.assert_objects(League, count=2)

        self.assert_command('import_games')

        for league in leagues:
            self.assertGreater(league.game_set.count(), 0, msg=f"league without games: {league}")


class Forfeit(IntegrationTestCase):
    def test_forfeit_with_report(self):
        self.assert_command('setup', '-a', 3, '-d', 10, '-s', 2018, '-l', 35537)

        self.assert_command('import_games', '-g', 60201)

        game: Game = self.assert_objects(Game)
        self.assertEqual(game.number, 60201)
        self.assertEqual(game.report_number, 710203)
        self.assertEqual(game.home_goals, 0)
        self.assertEqual(game.guest_goals, 0)
        self.assertEqual(game.forfeiting_team, game.guest_team)

    def test_forfeit_without_report(self):
        self.assert_command('setup', '-a', 35, '-d', 35, '-s', 2018, '-l', 34606)

        self.assert_command('import_games', '-g', 210348)

        game: Game = self.assert_objects(Game)
        self.assertEqual(game.number, 210348)
        self.assertEqual(game.report_number, None)
        self.assertEqual(game.home_goals, 0)
        self.assertEqual(game.guest_goals, 0)
        self.assertEqual(game.forfeiting_team, game.guest_team)


class Youth(IntegrationTestCase):
    def test_youth(self):
        test_setup_league.Youth.test_youth(self)

        self.assert_command('import_games', '--youth')

        league: League = self.assert_objects(League)
        self.assertGreater(league.game_set.count(), 0)

    def test_no_youth(self):
        test_setup_league.Youth.test_youth(self)

        self.assert_command('import_games')

        self.assert_objects(Game, count=0)


class BuggedGameRows(IntegrationTestCase):
    def test_additional_heading_row(self):
        self.assert_command('setup', '-a', 3, '-d', 8, '-s', 2019, '-l', 46786)
        self.assert_command('import_games', '-g', 41013)
        self.assert_objects(Game)
