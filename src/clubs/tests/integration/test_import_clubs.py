from associations.models import Association
from base.tests.base import IntegrationTestCase
from games.models import Team
from teams.models import Club


class ImportClubsTest(IntegrationTestCase):
    def test_no_associations(self):
        self.assert_command("import_clubs")
        self.assert_objects(Club, count=0)

    def test_no_associations_filtered(self):
        self.assert_command("import_associations", "-a", 3)
        self.assert_object(Association)

        self.assert_command("import_clubs", "-a", 0)
        self.assert_objects(Club, count=0)

    def test_single_association(self):
        self.assert_command("import_associations", "-a", 79)
        self.assert_object(Association)

        self.assert_command("import_clubs")
        self.assert_objects(Club, count=14)

    def test_single_association_filtered(self):
        self.assert_command("import_associations", "-a", 79, 4)
        self.assert_objects(Association, count=2)

        self.assert_command("import_clubs", "-a", 79)
        self.assert_objects(Club, count=14)

    def test_single_club_filtered(self):
        self.assert_command("import_associations", "-a", 95)
        association = self.assert_object(Association)

        self.assert_command("import_clubs", "-a", 95, "-c", 290002)
        club = self.assert_object(Club)

        self.assertEqual(club.name, "HC Berchem")
        self.assertTrue(club.associations.get(), association)
        self.assertEqual(club.bhv_id, 290002)

    def test_update_team(self):
        self.assert_command("import_associations", "-a", 80)
        self.assert_command("import_districts", "-d", 80)
        self.assert_command("import_leagues", "-s", 2023, "-l", 109051)

        team = self.assert_object(Team, filters={"bhv_id": 1036036})
        self.assertIsNone(team.club)

        self.assert_command("import_clubs", "-a", 80, "-c", 213031)

        actual = self.assert_object(Team, filters={"club__bhv_id": 213031})
        self.assertEqual(actual.bhv_id, team.bhv_id)
