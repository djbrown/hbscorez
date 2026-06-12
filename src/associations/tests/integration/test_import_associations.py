from associations.models import Association
from base.tests.base import IntegrationTestCase


class CommandTest(IntegrationTestCase):
    def test_specific(self):
        self.assert_command("import_associations", "-a", 95)
        association = self.assert_object(Association)
        self.assertEqual(association.name, "Fédération Luxembourgeoise de Handball")
        self.assertEqual(association.bhv_id, 95)
        self.assertEqual(association.abbreviation, "FLH")

    def test_update(self):
        Association.objects.create(
            name="Vorarlberger HV",
            abbreviation="vor",
            bhv_id=76,
            source_url="http://localhost",
        )

        self.assert_command("import_associations", "-a", 76)
        association = self.assert_object(Association)
        self.assertEqual(association.name, "Vorarlberger Handballverband")
        self.assertEqual(association.abbreviation, "VHV")
        self.assertEqual(association.bhv_id, 76)
        self.assertEqual(association.source_url, "https://www.handball4all.de/home/portal/vorarlberg")

    def test_all(self):
        self.assert_command("import_associations")
        self.assert_objects(Association, 2)
