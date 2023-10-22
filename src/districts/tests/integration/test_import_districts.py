from base.tests.base import IntegrationTestCase
from districts.models import District

class DistrictTest(IntegrationTestCase):
    def test__setup__district(self):
        self.assert_command('import_associations', '-a', 35)
        self.assert_command('import_districts', '-d', 35)
        district = self.assert_objects(District)
        self.assertEqual(district.bhv_id, 35)
        self.assertEqual(district.name, "Badischer Handball-Verband")

    def test__setup__district__single_association(self):
        self.assert_command('import_associations', '-a', 4, 35)
        self.assert_command('import_districts', '-a', 4)
        self.assert_objects(District, 4)

    def test__setup__district__update(self):
        District.objects.create(name="My District", bhv_id=35)

        self.assert_command('import_associations', '-a', 35)
        self.assert_command('import_districts', '-d', 35)

        district = self.assert_objects(District)
        self.assertEqual(district.name, "Badischer Handball-Verband")

    def test__setup__all_districts(self):
        self.assert_command('import_associations')
        self.assert_command('import_districts')
        self.assert_objects(District, count=65)
