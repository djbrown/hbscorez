from associations.models import Association
from base.tests.base import IntegrationTestCase
from districts.models import District
from leagues.models import League, Season


class SetupTest(IntegrationTestCase):

    def test__setup__association(self):
        self.assert_command('setup', '-a', 35, '-d', 0)
        association = self.assert_objects(Association)
        self.assertEqual(association.bhv_id, 35)
        self.assertEqual(association.name, "Badischer Handball-Verband")

    def test__setup__all_associations_and_districts(self):
        self.assert_command('setup', '-s', 0)
        self.assert_objects(Association, count=14)
        self.assert_objects(District, count=65)

    def test__setup__oberliga_hamburg_schleswig(self):
        self.assert_command('setup', '-a', 77, '-d', 77, '-s', 2021, '-l', 77606)
        self.assert_objects(League)

    def test__setup__district(self):
        self.assert_command('setup', '-a', 35, '-d', 35, '-s', 0)
        district = self.assert_objects(District)
        self.assertEqual(district.bhv_id, 35)
        self.assertEqual(district.name, "BHV-Ligen")

    def test__setup__season(self):
        self.assert_command('setup', '-a', 35, '-d', 35, '-s', 2017, '-l', 0)

        season = self.assert_objects(Season)
        self.assertEqual(season.start_year, 2017)

    def test__setup__league(self):
        self.assert_command('setup', '-a', 35, '-d', 35, '-s', 2017, '-l', 26777)

        league = self.assert_objects(League)
        self.assertEqual(league.name, "Verbandsliga Männer")
        self.assertEqual(league.abbreviation, "M-VL")
        self.assertEqual(league.bhv_id, 26777)

    def test__setup__exclude_irrelevant_seasons(self):
        self.assert_command('setup', '-a', 4, '-d', 3, '-l', 0)
        self.assert_objects(League, 0)

        for start_year in range(2004, 2019):
            exists = Season.objects.filter(start_year=start_year).exists()
            self.assertTrue(exists, f'Season {start_year} should exist')

    def test__setup__old_leagues(self):
        self.assert_command('setup', '-a', 4, '-d', 3, '-l', 0)

        self.assert_objects(League, count=0)

        for start_year in range(1999, 2004):
            exists = Season.objects.filter(start_year=start_year).exists()
            self.assertFalse(exists, f'Season {start_year} should not exist')

    def test__setup__meisterschaft(self):
        self.assert_command('setup', '-a', 3, '-d', 3, '-s', 2009, '-l', 9656, 9657, 10677)

        self.assert_command('import_games')

    def test__setup__subsequently_added_to_district(self):
        self.assert_command('setup', '-a', 35, '-d', 35, '-s', 2019, '-l', 53980)
        self.assert_command('setup', '-a', 4, '-d', 4, '-s', 2019, '-l', 53980)


class StartDate(IntegrationTestCase):
    def test_first_hit(self):
        self.assert_command('setup', '-a', 80, '-d', 80, '-s', 2018, '-l', 34744)

        self.assert_objects(League, count=1)

    def test_first_hit_multiseason(self):
        self.assert_command('setup', '-a', 80, '-d', 80, '-s', 2017, 2018, '-l', 27265, 34744)

        self.assert_objects(League, count=2)

    def test_later_hit(self):
        self.assert_command('setup', '-a', 81, '-d', 81, '-s', 2018, '-l', 37511)

        self.assert_objects(League, count=1)

    def test_later_hit_multiseason(self):
        self.assert_command('setup', '-a', 81, '-d', 81, '-s', 2017, 2018, '-l', 30859, 37511)

        self.assert_objects(League, count=2)
