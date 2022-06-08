
from base.tests.base import IntegrationTestCase
from leagues.models import League, LeagueName, Season


class SetupTest(IntegrationTestCase):

    def test__setup__mvl_2016(self):
        self.assert_command('setup', '-a', 35, '-d', 35, '-s', 2016, '-l', 21666)

        season = self.assert_objects(Season)
        self.assertEqual(season.start_year, 2016)

        league = self.assert_objects(League)
        self.assertEqual(league.name, "Verbandsliga Männer")
        self.assertEqual(league.abbreviation, "M-VL")
        self.assertEqual(league.bhv_id, 21666)
        self.assertEqual(league.season, season)

    def test__setup__mvl_2017(self):
        self.assert_command('setup', '-a', 35, '-d', 35, '-s', 2017, '-l', 26777)

        season = self.assert_objects(Season)
        self.assertEqual(season.start_year, 2017)

        league = self.assert_objects(League)
        self.assertEqual(league.name, "Verbandsliga Männer")
        self.assertEqual(league.abbreviation, "M-VL")
        self.assertEqual(league.bhv_id, 26777)
        self.assertEqual(league.season, season)

    def test__setup__mwls_2016(self):
        self.assert_command('setup', '-a', 3, '-d', 3, '-s', 2016, '-l', 21747)

        season = self.assert_objects(Season)
        self.assertEqual(season.start_year, 2016)

        league = self.assert_objects(League)
        self.assertEqual(league.name, "Männer Württemberg-Liga Süd")
        self.assertEqual(league.abbreviation, "M-WL-S")
        self.assertEqual(league.bhv_id, 21747)
        self.assertEqual(league.season, season)

    def test__setup__mwls_2017(self):
        self.assert_command('setup', '-a', 3, '-d', 3, '-s', 2017, '-l', 27505)

        season = self.assert_objects(Season)
        self.assertEqual(season.start_year, 2017)

        league = self.assert_objects(League)
        self.assertEqual(league.name, "Männer Württemberg-Liga Süd")
        self.assertEqual(league.abbreviation, "M-WL-S")
        self.assertEqual(league.bhv_id, 27505)
        self.assertEqual(league.season, season)

    def test__setup__mklc2_2007(self):
        LeagueName.objects.create(bhv_id=7424, name="Männer Kreisliga C Staffel 3")

        self.assert_command('setup', '-a', 3, '-d', 7, '-s', 2007, '-l', 7423, 7424)

        self.assert_objects(League, count=2)
        mklc2 = League.objects.get(abbreviation="M-KLC-2")
        mklc3 = League.objects.get(abbreviation="M-KLC-3")

        self.assertEqual(mklc2.name, "Männer Kreisliga C Staffel 2")
        self.assertEqual(mklc3.name, "Männer Kreisliga C Staffel 3")

    def test__setup__mkl2_2005(self):
        LeagueName.objects.create(bhv_id=5380, name="Männer Kreisliga 2-1")
        LeagueName.objects.create(bhv_id=5381, name="Männer Kreisliga 2-2")

        self.assert_command('setup', '-a', 3, '-d', 10, '-s', 2005, '-l', 5380, 5381)

        self.assert_objects(League, count=2)
        mkl21 = League.objects.get(abbreviation="M-KL2-1")
        mkl22 = League.objects.get(abbreviation="M-KL2-2")

        self.assertEqual(mkl21.name, "Männer Kreisliga 2-1")
        self.assertEqual(mkl22.name, "Männer Kreisliga 2-2")


class Youth(IntegrationTestCase):
    def test_youth(self):
        self.assert_command('setup', '-a', 35, '-d', 35, '-s', 2019, '-l', 46921, '--youth')

        league: League = self.assert_objects(League)
        self.assertTrue(league.youth)

    def test_no_youth(self):
        self.assert_command('setup', '-a', 35, '-d', 35, '-s', 2019, '-l', 46921)

        self.assert_objects(League, count=0)


class LongLeagueNames(IntegrationTestCase):
    def test_youth(self):
        self.assert_command('setup', '-a', 83, '-d', 83, '-s', 2019, '-l', 45646, 45651, '--youth')

        leagues = self.assert_objects(League, count=2).order_by('name')
        self.assertEqual(leagues[0].name, 'männliche Jgd. B - Kreisklasse')
        self.assertEqual(leagues[1].name, 'männliche Jgd. B - Rheinhessenliga')


class Pokal(IntegrationTestCase):
    def test_fpokk_2019(self):
        self.assert_command('setup', '-a', 56, '-d', 62, '-s', 2019, '-l', 45411)

        self.assert_objects(League, count=0)
