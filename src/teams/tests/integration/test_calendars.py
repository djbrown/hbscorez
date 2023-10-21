from base.tests.base import IntegrationTestCase

from teams.models import Team


class CalendarTest(IntegrationTestCase):
    def test__rems_stuttgart__mkld(self):
        self.assert_command('import_associations', '-a', 3)
        self.assert_command('setup', '-d', 7, '-s', 2017, '-l', 28454)
        self.assert_command('import_games')

        self.client.get('/mannschaften/391930/kalender/')

        self.assert_objects(Team, count=1, filters={'retirement__isnull': False})
