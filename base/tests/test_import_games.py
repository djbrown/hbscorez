import datetime

from django.core.management import call_command
from django.test import TestCase

from base import models


class ImportGamesTest(TestCase):

    def test__import_games__specific_game(self):
        return_code = call_command('setup', '-a 35', '-d 35', '-s 2017', '-l 26777')
        self.assertEqual(return_code, None)

        return_code = call_command('import_games', '-g 210226')
        self.assertEqual(return_code, None)

        games = models.Game.objects.all()
        self.assertEqual(len(games), 1)

        game = games[0]
        self.assertEqual(game.number, 210226)
        self.assertEqual(game.opening_whistle, datetime.datetime(2017, 10, 7, 19, 45))
        self.assertEqual(game.home_team.short_name, 'TSVG Malsch')
        self.assertEqual(game.guest_team.short_name, 'HSG Dittig/TBB')
        self.assertEqual(game.home_goals, 24)
        self.assertEqual(game.guest_goals, 22)
        self.assertEqual(game.report_number, 490394)
        self.assertEqual(game.sports_hall.number, 22010)

    def test__import_games__m_vl(self):
        return_code = call_command('setup', '-a 35', '-d 35', '-s 2017', '-l 26777')
        self.assertEqual(return_code, None)

        return_code = call_command('import_games')
        self.assertEqual(return_code, None)

        games = models.Game.objects.all()
        self.assertEqual(len(games), 182)

    def test__import_games__missing_district(self):
        return_code = call_command('import_games', '-a 35', '-d 0')
        self.assertEqual(return_code, None)

        games = models.Game.objects.all()
        self.assertEqual(len(games), 0)
