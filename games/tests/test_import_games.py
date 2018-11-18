import datetime

from django.core.management import call_command

from base.tests.model_test_case import ModelTestCase
from games.models import Game
from leagues.models import League


class ImportGamesTest(ModelTestCase):

    def test__import_games__specific_game(self):
        return_code = call_command('setup', '-a', 35, '-d', 35, '-s', 2017, '-l', 26777)
        self.assertEqual(return_code, None)
        league = self.assert_objects(League)

        return_code = call_command('import_games', '-g', 210226)
        self.assertEqual(return_code, None)
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
        return_code = call_command('setup', '-a', 35, '-d', 35, '-s', 2017, '-l', 26777)
        self.assertEqual(return_code, None)
        self.assert_objects(League)

        return_code = call_command('import_games')
        self.assertEqual(return_code, None)
        self.assert_objects(Game, 182)

    def test__import_games__missing_district(self):
        return_code = call_command('import_games', '-a', 35, '-d', 0)
        self.assertEqual(return_code, None)
        self.assert_objects(Game, 0)
