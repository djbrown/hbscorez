from associations.models import Association
from base.tests.base import IntegrationTestCase
from districts.models import District


class CommandTest(IntegrationTestCase):
    def test_specific_district(self):
        association = Association.objects.create(bhv_id=95)

        self.assert_command("import_districts", "-d", 95)

        district = self.assert_object(District)
        self.assertEqual(district.bhv_id, 95)
        self.assertEqual(district.name, "Fédération Luxembourgeoise de Handball")
        self.assertEqual(list(district.associations.all()), [association])

    def test_stored_association(self):
        association = Association.objects.create(bhv_id=95)

        self.assert_command("import_districts")

        district = self.assert_object(District)
        self.assertEqual(district.associations.first(), association)

    def test_specific_stored_association(self):
        Association.objects.create(bhv_id=95)
        association = Association.objects.create(bhv_id=76)

        self.assert_command("import_districts", "-a", 76)

        districts = self.assert_objects(District, 3)
        self.assertEqual(set(association.district_set.all()), set(districts))

    def test_specific_unstored_association(self):
        Association.objects.create(bhv_id=95, name="95")
        self.assert_command("import_districts", "-a", 76)

        self.assert_objects(District, 0)

    def test_specific_nonexisting_district(self):
        Association.objects.create(bhv_id=95, name="95")
        self.assert_command("import_districts", "-d", 6000)

        self.assert_objects(District, 0)

    def test_update_specific_stored_district(self):
        Association.objects.create(bhv_id=76)
        District.objects.create(name="My District", bhv_id=12)

        self.assert_command("import_districts", "-d", 12)

        district = self.assert_object(District)
        self.assertEqual(district.name, "Bodensee-Donau")

    def test_all_existing_districts(self):
        self.assert_command("import_associations")
        self.assert_command("import_districts")
        self.assert_objects(District, count=4)
