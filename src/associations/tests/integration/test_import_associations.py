from associations.models import Association
from base.tests.base import IntegrationTestCase


class CommandTest(IntegrationTestCase):
    def test_specific(self):
        self.assert_command("import_associations", "-a", 35)
        association = self.assert_object(Association)
        self.assertEqual(association.name, "Badischer Handball-Verband")
        self.assertEqual(association.bhv_id, 35)
        self.assertEqual(association.abbreviation, None)

    def test_update(self):
        Association.objects.create(
            name="Badischer HV",
            abbreviation="Test",
            bhv_id=35,
            source_url="http://localhost",
        )

        self.assert_command("import_associations", "-a", 35)
        association = self.assert_object(Association)
        self.assertEqual(association.name, "Badischer Handball-Verband")
        self.assertEqual(association.abbreviation, "Test")
        self.assertEqual(association.bhv_id, 35)
        self.assertEqual(association.source_url, "https://www.handball4all.de/home/portal/baden")

    def test_all(self):
        self.assert_command("import_associations")
        self.assert_objects(Association, 14)
