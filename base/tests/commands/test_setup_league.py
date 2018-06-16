from django.core.management import call_command

from base import models
from base.tests.model_test_case import ModelTestCase


class SetupTest(ModelTestCase):

    def test__setup__mvl_2016(self):
        return_code = call_command('setup', '-a 35', '-d 35', '-s 2016', '-l 21666')
        self.assertEqual(return_code, None)

        season = self.assert_objects(models.Season)
        self.assertEqual(season.start_year, 2016)

        league = self.assert_objects(models.League)
        self.assertEqual(league.name, "Verbandsliga Männer")
        self.assertEqual(league.abbreviation, "M-VL")
        self.assertEqual(league.bhv_id, 21666)
        self.assertEqual(league.season, season)

    def test__setup__mvl_2017(self):
        return_code = call_command('setup', '-a 35', '-d 35', '-s 2017', '-l 26777')
        self.assertEqual(return_code, None)

        season = self.assert_objects(models.Season)
        self.assertEqual(season.start_year, 2017)

        league = self.assert_objects(models.League)
        self.assertEqual(league.name, "Verbandsliga Männer")
        self.assertEqual(league.abbreviation, "M-VL")
        self.assertEqual(league.bhv_id, 26777)
        self.assertEqual(league.season, season)

    def test__setup__mwls_2016(self):
        return_code = call_command('setup', '-a 3', '-d 3', '-s 2016', '-l 21747')
        self.assertEqual(return_code, None)

        season = self.assert_objects(models.Season)
        self.assertEqual(season.start_year, 2016)

        league = self.assert_objects(models.League)
        self.assertEqual(league.name, "Männer Württemberg-Liga Süd")
        self.assertEqual(league.abbreviation, "M-WL-S")
        self.assertEqual(league.bhv_id, 21747)
        self.assertEqual(league.season, season)

    def test__setup__mwls_2017(self):
        return_code = call_command('setup', '-a 3', '-d 3', '-s 2017', '-l 27505')
        self.assertEqual(return_code, None)

        season = self.assert_objects(models.Season)
        self.assertEqual(season.start_year, 2017)

        league = self.assert_objects(models.League)
        self.assertEqual(league.name, "Männer Württemberg-Liga Süd")
        self.assertEqual(league.abbreviation, "M-WL-S")
        self.assertEqual(league.bhv_id, 27505)
        self.assertEqual(league.season, season)
