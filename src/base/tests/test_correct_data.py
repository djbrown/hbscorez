import datetime

from django.core.management import call_command

from base.tests.model_test_case import ModelTestCase
from games.models import Game
from leagues.models import League
from players.models import Score


class ImportGamesTest(ModelTestCase):

    def test_game_210116_sghh_hcn(self):
        return_code = call_command('setup', '-a', 35, '-d', 35, '-s', 2017, '-l', 26773)
        self.assertEqual(return_code, None)
        league = self.assert_objects(League)

        return_code = call_command('import_games', '-g', 210116)
        self.assertEqual(return_code, None)
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

        return_code = call_command('correct_data')
        self.assertEqual(return_code, None)

        self.assert_objects(Score, 26)
