from django.core.management import call_command

from associations.models import Association
from base.tests.model_test_case import ModelTestCase
from districts.models import District
from leagues.models import League, Season


class SetupTest(ModelTestCase):

    def test__setup__association(self):
        return_code = call_command('setup', '-a', 35, '-d', 0)
        self.assertEqual(return_code, None)
        association = self.assert_objects(Association)
        self.assertEqual(association.bhv_id, 35)
        self.assertEqual(association.name, "Badischer Handball-Verband")

    def test__setup__district(self):
        return_code = call_command('setup', '-a', 35, '-d', 35, '-s', 0)
        self.assertEqual(return_code, None)
        district = self.assert_objects(District)
        self.assertEqual(district.bhv_id, 35)
        self.assertEqual(district.name, "BHV-Ligen")

    def test__setup__season(self):
        return_code = call_command('setup', '-a', 35, '-d', 35, '-s', 2017, '-l', 0)
        self.assertEqual(return_code, None)

        season = self.assert_objects(Season)
        self.assertEqual(season.start_year, 2017)

    def test__setup__league(self):
        return_code = call_command('setup', '-a', 35, '-d', 35, '-s', 2017, '-l', 26777)
        self.assertEqual(return_code, None)

        league = self.assert_objects(League)
        self.assertEqual(league.name, "Verbandsliga Männer")
        self.assertEqual(league.abbreviation, "M-VL")
        self.assertEqual(league.bhv_id, 26777)

    def test__setup__exclude_irrelevant_seasons(self):
        return_code = call_command('setup', '-a', 4, '-d', 3, '-l', 0)
        self.assertEqual(return_code, None)
        self.assert_objects(League, 0)

        for start_year in range(2004, 2019):
            exists = Season.objects.filter(start_year=start_year).exists()
            self.assertTrue(exists, 'Season {} should exist'.format(start_year))

    def test__setup__old_leagues(self):
        return_code = call_command('setup', '-a', 4, '-d', 3, '-l', 0)
        self.assertEqual(return_code, None)

        self.assert_objects(League, count=0)

        for start_year in range(1999, 2004):
            exists = Season.objects.filter(start_year=start_year).exists()
            self.assertFalse(exists, 'Season {} should not exist'.format(start_year))

    def test__setup__meisterschaft(self):
        return_code = call_command('setup', '-a', 3, '-d', 3, '-s', 2009, '-l', 9656, 9657, 10677)
        self.assertEqual(return_code, None)

        return_code = call_command('import_games')
        self.assertEqual(return_code, None)


class StartDate(ModelTestCase):
    def test_first_hit(self):
        return_code = call_command('setup', '-a', 80, '-d', 80, '-s',  2018, '-l',  34744)
        self.assertEqual(return_code, None)

        self.assert_objects(League, count=1)

    def test_first_hit_multiseason(self):
        return_code = call_command('setup', '-a', 80, '-d', 80, '-s', 2017, 2018, '-l', 27265, 34744)
        self.assertEqual(return_code, None)

        self.assert_objects(League, count=2)

    def test_later_hit(self):
        return_code = call_command('setup', '-a', 81, '-d', 81, '-s',  2018, '-l', 37511)
        self.assertEqual(return_code, None)

        self.assert_objects(League, count=1)

    def test_later_hit_multiseason(self):
        return_code = call_command('setup', '-a', 81, '-d', 81, '-s', 2017, 2018, '-l', 30859, 37511)
        self.assertEqual(return_code, None)

        self.assert_objects(League, count=2)
