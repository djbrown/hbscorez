from django.core.management import call_command

from base import models
from base.tests.model_test_case import ModelTestCase


class SetupTest(ModelTestCase):

    def test__setup__association(self):
        return_code = call_command('setup', '-a 35', '-d 0')
        self.assertEqual(return_code, None)
        association = self.assert_objects(models.Association)
        self.assertEqual(association.bhv_id, 35)
        self.assertEqual(association.name, "Badischer Handball-Verband")

    def test__setup__district(self):
        return_code = call_command('setup', '-a 35', '-d 35', '-s 0')
        self.assertEqual(return_code, None)
        district = self.assert_objects(models.District)
        self.assertEqual(district.bhv_id, 35)
        self.assertEqual(district.name, "BHV-Ligen")

    def test__setup__season(self):
        return_code = call_command('setup', '-a 35', '-d 35', '-s 2017', '-l 0')
        self.assertEqual(return_code, None)

        season = self.assert_objects(models.Season)
        self.assertEqual(season.start_year, 2017)

    def test__setup__league(self):
        return_code = call_command('setup', '-a 35', '-d 35', '-s 2017', '-l 26777')
        self.assertEqual(return_code, None)

        league = self.assert_objects(models.League)
        self.assertEqual(league.name, "Verbandsliga Männer")
        self.assertEqual(league.abbreviation, "M-VL")
        self.assertEqual(league.bhv_id, 26777)

    def test__setup__exclude_irrelevant_seasons(self):
        return_code = call_command('setup', '-a 4', '-d 3', '-l 0')
        self.assertEqual(return_code, None)
        self.assert_objects(models.League, 0)

        for start_year in range(1999, 2018):
            exists = models.Season.objects.filter(start_year=start_year).exists()
            self.assertTrue(exists, 'Season {} does not exist'.format(start_year))
