from datetime import timedelta
from unittest.mock import Mock, patch

from base.tests.base import IntegrationTestCase
from games.tests.integration import test_import_games
from players.models import Player, ReportsBlacklist, Score


class TestImportReport(IntegrationTestCase):
    def test_successful(self):
        self.assert_command('setup', '-a', 77, '-d', 77, '-s', 2021, '-l', 77606)
        self.assert_command('import_games', '-g', 10001127)
        self.assert_command('import_reports')

        scores = self.assert_objects(Score, count=28)
        self.assertEqual(scores[0].game.report_number, 1525036)
        self.assertEqual(scores[0].game.spectators, 251)

        score: Score = scores.get(player_number=24)
        self.assertEqual(score.goals, 10)
        self.assertEqual(score.penalty_goals, 7)
        self.assertEqual(score.penalty_tries, 7)
        self.assertEqual(score.warning_time, timedelta(minutes=7, seconds=7))
        self.assertEqual(score.first_suspension_time, timedelta(minutes=25, seconds=1))
        self.assertEqual(score.second_suspension_time, None)
        self.assertEqual(score.third_suspension_time, None)
        self.assertEqual(score.disqualification_time, None)
        self.assertEqual(score.report_time, None)
        self.assertEqual(score.team_suspension_time, None)


class Forfeit(IntegrationTestCase):

    def test(self):
        self.assert_command('setup', '-a', 3, '-d', 10, '-s', 2018, '-l', 35537)

        self.assert_command('import_games', '-g', 60201)

        mock: Mock
        with patch('players.management.commands.import_reports.import_report') as mock:
            self.assert_command('import_reports')
            mock.assert_not_called()


class Youth(IntegrationTestCase):
    def test_youth(self):
        test_import_games.Youth.test_youth(self)

        self.assert_command('import_reports')

        self.assert_objects(Score, count=0)
        self.assert_objects(Player, count=0)


class ReportsBlacklistTest(IntegrationTestCase):
    def test_blacklist(self):

        self.assert_command('setup', '-a', 78, '-d', 121, '-s', 2021, '-l', 69541)
        self.assert_command('import_games', '-g', 603101155)
        ReportsBlacklist.objects.create(report_number=1592331)
        self.assert_command('import_reports')

        self.assert_objects(Score, count=0)
        self.assert_objects(Player, count=0)
