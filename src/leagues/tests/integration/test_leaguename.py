from django.core import mail

from base.tests.base import IntegrationTestCase
from leagues.models import League, LeagueName


class IgnoredName(IntegrationTestCase):

    def test_ignored_name(self):
        LeagueName.objects.create(bhv_id=91991, name="EN-Turnier")

        self.assert_command('import_associations', '-a', 78)
        self.assert_command('setup', '-d', 161, '-s', 2022, '-l', 91991)

        self.assert_objects(League, count=0)
        self.assertEqual(len(mail.outbox), 0)
