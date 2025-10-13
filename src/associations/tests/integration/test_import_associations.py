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
            name="Test Name",
            short_name="Baden",
            source_url="http://localhost/test/url",
            abbreviation="Test-Abbreviation",
        )

        self.assert_command("import_associations", "-a", "Baden")
        association = self.assert_object(Association)
        self.assertEqual(association.name, "Badischer Handball-Verband")
        self.assertEqual(association.short_name, "Baden")
        self.assertEqual(association.source_url, "https://www.handball.net/verbaende/Baden")
        self.assertEqual(association.abbreviation, "Test-Abbreviation")

    def test_all(self):
        self.assert_command("import_associations")
        self.assert_objects(Association, 25)
