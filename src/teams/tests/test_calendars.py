from django.core.management import call_command
from base.tests.model_test_case import ModelTestCase

from teams.models import Team


class CalendarTest(ModelTestCase):
    def test__rems_stuttgart__mkld(self):
        call_command('setup', '-a', 3, '-d', 7, '-s', 2017, '-l', 28454)
        call_command('import_games')

        self.client.get('/mannschaften/391930/kalender/')

        self.assert_objects(Team, count=1, filters={'retirement__isnull': False})
