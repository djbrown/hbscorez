from associations.models import Association
from base.tests.base import IntegrationTestCase


class CommandTest(IntegrationTestCase):
    def test_specific(self):
        self.assert_command("import_associations", "-a", "Baden")
        association = self.assert_object(Association)
        self.assertEqual(association.name, "Badischer Handball-Verband")
        self.assertEqual(association.short_name, "Baden")
        self.assertEqual(association.abbreviation, None)

    def test_update(self):
        Association.objects.create(
            name="Badischer HV",
            short_name="Short",
            source_url="http://localhost",
            abbreviation="Test",
        )

        self.assert_command("import_associations", "-a", "Baden")
        association = self.assert_object(Association)
        self.assertEqual(association.name, "Badischer Handball-Verband")
        self.assertEqual(association.short_name, "Baden")
        self.assertEqual(association.source_url, "https://www.handball4all.de/home/portal/baden")
        self.assertEqual(association.abbreviation, "Test")

    def test_all(self):
        self.assert_command("import_associations")
        self.assert_objects(Association, 14)
