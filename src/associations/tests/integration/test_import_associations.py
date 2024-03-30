from associations.models import Association
from base.tests.base import IntegrationTestCase


class CommandTest(IntegrationTestCase):
    def test_specific(self):
        self.assert_command("import_associations", "-a", 35)
        association = self.assert_objects(Association)
        self.assertEqual(association.name, "Badischer Handball-Verband")
        self.assertEqual(association.abbreviation, "BHV")
        self.assertEqual(association.bhv_id, 35)

    def test_update(self):
        Association.objects.create(
            name="Badischer HV",
            abbreviation="bad",
            bhv_id=35,
            source_url="http://localhost",
        )

        self.assert_command("import_associations", "-a", 35)
        association = self.assert_objects(Association)
        self.assertEqual(association.name, "Badischer Handball-Verband")
        self.assertEqual(association.abbreviation, "bad")
        self.assertEqual(association.bhv_id, 35)

    def test_all(self):
        self.assert_command("import_associations")
        self.assert_objects(Association, 14)
