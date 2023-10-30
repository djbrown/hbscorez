import datetime

from base.tests.base import IntegrationTestCase
from games.models import Game
from leagues.models import League
from players.models import Score


class ImportGamesTest(IntegrationTestCase):
    def test_game_210116_sghh_hcn(self):
        self.assert_command('import_associations', '-a', 35)
        self.assert_command('import_districts', '-d', 35)
        self.assert_command('import_leagues', '-s', 2017, '-l', 26773)
        league = self.assert_objects(League)

        self.assert_command('import_games', '-g', 210116)
        game = self.assert_objects(Game)

        self.assertEqual(game.number, 210116)
        self.assertEqual(game.opening_whistle, datetime.datetime(2018, 2, 18, 17, 30))
        self.assertEqual(game.home_team.short_name, 'SG Heidel/Helm')
        self.assertEqual(game.guest_team.short_name, 'HC Neuenbürg')
        self.assertEqual(game.home_goals, 29)
        self.assertEqual(game.guest_goals, 35)
        self.assertIsNone(game.report_number)
        self.assertEqual(game.sports_hall.number, 21004)
        self.assertEqual(game.league, league)

        self.assert_objects(Score, 0)

        self.assert_command('correct_data')

        self.assert_objects(Score, 26)

    def test_game_96781(self):
        self.assert_command('import_associations', '-a', 3)
        self.assert_command('import_districts', '-d', 3)
        self.assert_command('import_leagues', '-s', 2019, '-l', 45956)
        league = self.assert_objects(League)

        self.assert_command('import_games', '-g', 96781)
        game = self.assert_objects(Game)

        self.assertEqual(game.number, 96781)
        self.assertEqual(game.opening_whistle, datetime.datetime(2019, 9, 14, 19, 00))
        self.assertEqual(game.home_team.short_name, 'TV Weingarten')
        self.assertEqual(game.guest_team.short_name, 'SG Argental')
        self.assertEqual(game.home_goals, 19)
        self.assertEqual(game.guest_goals, 23)
        self.assertIsNone(game.report_number)
        self.assertEqual(game.sports_hall.number, 8092)
        self.assertEqual(game.league, league)

        self.assert_objects(Score, 0)

        self.assert_command('correct_data')

        self.assert_objects(Score, 27)
