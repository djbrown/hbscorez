from associations.models import Association
from base.tests.base import IntegrationTestCase
from teams.models import Club


class ImportClubsTest(IntegrationTestCase):
    def test_no_associations(self):
        self.assert_command('import_clubs')
        self.assert_objects(Club, count=0)

    def test_no_associations_filtered(self):
        self.assert_command('import_associations', '-a', 3)
        self.assert_objects(Association)

        self.assert_command('import_clubs', '-a', 0)
        self.assert_objects(Club, count=0)

    def test_single_association(self):
        self.assert_command('import_associations', '-a', 79)
        self.assert_objects(Association)

        self.assert_command('import_clubs')
        self.assert_objects(Club, count=11)

    def test_single_association_filtered(self):
        self.assert_command('import_associations', '-a', 79, 4)
        self.assert_objects(Association, count=2)

        self.assert_command('import_clubs', '-a', 79)
        self.assert_objects(Club, count=11)

    def test_single_club_filtered(self):
        self.assert_command('import_associations', '-a', 95)
        association = self.assert_objects(Association)

        self.assert_command('import_clubs', '-a', 95, '-c', 9702)
        club = self.assert_objects(Club)

        self.assertEqual(club.name, 'Lettland')
        self.assertTrue(club.associations.get(), association)
        self.assertEqual(club.bhv_id, 9702)