from unittest.mock import Mock, patch

from base.tests.base import IntegrationTestCase
from games.tests.integration import test_import_games
from players.models import Player, ReportsBlacklist, Score


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
