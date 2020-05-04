from unittest.mock import Mock, patch

from base.tests.base import IntegrationTestCase
from games.tests.integration import test_import_games
from players.models import Player, Score


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
