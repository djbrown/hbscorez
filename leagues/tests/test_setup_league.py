from django.core.management import call_command

from base.tests.model_test_case import ModelTestCase
from leagues.models import League, Season


class SetupTest(ModelTestCase):

    def test__setup__mvl_2016(self):
        return_code = call_command('setup', '-a', 35, '-d', 35, '-s', 2016, '-l', 21666)
        self.assertEqual(return_code, None)

        season = self.assert_objects(Season)
        self.assertEqual(season.start_year, 2016)

        league = self.assert_objects(League)
        self.assertEqual(league.name, "Verbandsliga Männer")
        self.assertEqual(league.abbreviation, "M-VL")
        self.assertEqual(league.bhv_id, 21666)
        self.assertEqual(league.season, season)

    def test__setup__mvl_2017(self):
        return_code = call_command('setup', '-a', 35, '-d', 35, '-s', 2017, '-l', 26777)
        self.assertEqual(return_code, None)

        season = self.assert_objects(Season)
        self.assertEqual(season.start_year, 2017)

        league = self.assert_objects(League)
        self.assertEqual(league.name, "Verbandsliga Männer")
        self.assertEqual(league.abbreviation, "M-VL")
        self.assertEqual(league.bhv_id, 26777)
        self.assertEqual(league.season, season)

    def test__setup__mwls_2016(self):
        return_code = call_command('setup', '-a', 3, '-d', 3, '-s', 2016, '-l', 21747)
        self.assertEqual(return_code, None)

        season = self.assert_objects(Season)
        self.assertEqual(season.start_year, 2016)

        league = self.assert_objects(League)
        self.assertEqual(league.name, "Männer Württemberg-Liga Süd")
        self.assertEqual(league.abbreviation, "M-WL-S")
        self.assertEqual(league.bhv_id, 21747)
        self.assertEqual(league.season, season)

    def test__setup__mwls_2017(self):
        return_code = call_command('setup', '-a', 3, '-d', 3, '-s', 2017, '-l', 27505)
        self.assertEqual(return_code, None)

        season = self.assert_objects(Season)
        self.assertEqual(season.start_year, 2017)

        league = self.assert_objects(League)
        self.assertEqual(league.name, "Männer Württemberg-Liga Süd")
        self.assertEqual(league.abbreviation, "M-WL-S")
        self.assertEqual(league.bhv_id, 27505)
        self.assertEqual(league.season, season)

    def test__setup__mklc2_2007(self):
        return_code = call_command('setup', '-a', 3, '-d', 7, '-s', 2007, '-l', 7423, 7424)
        self.assertEqual(return_code, None)

        self.assert_objects(League, count=2)
        mklc2 = League.objects.get(abbreviation="M-KLC-2")
        mklc3 = League.objects.get(abbreviation="M-KLC-3")

        self.assertEqual(mklc2.name, "Männer Kreisliga C Staffel 2")
        self.assertEqual(mklc3.name, "Männer Kreisliga C Staffel 3")

    def test__setup__mkl2_2005(self):
        return_code = call_command('setup', '-a', 3, '-d', 10, '-s', 2005, '-l', 5380, 5381)
        self.assertEqual(return_code, None)

        self.assert_objects(League, count=2)
        mkl21 = League.objects.get(abbreviation="M-KL2-1")
        mkl22 = League.objects.get(abbreviation="M-KL2-2")

        self.assertEqual(mkl21.name, "Männer Kreisliga 2-1")
        self.assertEqual(mkl22.name, "Männer Kreisliga 2-2")
