from base.tests.base import IntegrationTestCase
from districts.models import District
from leagues.models import League, Season


class SeasonTest(IntegrationTestCase):
    def test__setup__season(self):
        self.assert_command('import_associations', '-a', 35)
        self.assert_command('import_districts', '-d', 35)
        self.assert_command('setup', '-s', 2017, '-l', 0)

        season = self.assert_objects(Season)
        self.assertEqual(season.start_year, 2017)

    def test__setup__exclude_irrelevant_seasons(self):
        self.assert_command('import_associations', '-a', 4)
        self.assert_command('import_districts', '-d', 3)
        self.assert_command('setup', '-l', 0)
        self.assert_objects(League, 0)

        for start_year in range(2004, 2019):
            exists = Season.objects.filter(start_year=start_year).exists()
            self.assertTrue(exists, f'Season {start_year} should exist')

    def test__setup__old_seasons(self):
        self.assert_command('import_associations', '-a', 4)
        self.assert_command('import_districts', '-d', 3)
        self.assert_command('setup', '-l', 0)

        self.assert_objects(League, count=0)

        for start_year in range(1999, 2004):
            exists = Season.objects.filter(start_year=start_year).exists()
            self.assertFalse(exists, f'Season {start_year} should not exist')


class LeagueTest(IntegrationTestCase):
    def test__setup__league(self):
        self.assert_command('import_associations', '-a', 35)
        self.assert_command('import_districts', '-d', 35)
        self.assert_command('setup', '-s', 2017, '-l', 26777)

        league = self.assert_objects(League)
        self.assertEqual(league.name, "Verbandsliga Männer")
        self.assertEqual(league.abbreviation, "M-VL")
        self.assertEqual(league.bhv_id, 26777)

    def test__setup__league__update(self):
        self.assert_command('import_associations', '-a', 35)
        self.assert_command('import_districts', '-d', 35)
        district = self.assert_objects(District)
        season = Season.objects.create(start_year=2017)
        League.objects.create(name="My League", abbreviation="ABBR", district=district, season=season, bhv_id=26777)

        self.assert_command('setup', '-s', 2017, '-l', 26777)

        league = self.assert_objects(League)
        self.assertEqual(league.name, "Verbandsliga Männer")
        self.assertEqual(league.abbreviation, "M-VL")
        self.assertEqual(league.bhv_id, 26777)

    def test__setup__oberliga_hamburg_schleswig(self):
        self.assert_command('import_associations', '-a', 77)
        self.assert_command('import_districts', '-d', 77)
        self.assert_command('setup', '-s', 2021, '-l', 77606)
        self.assert_objects(League)

    def test__setup__meisterschaft(self):
        self.assert_command('import_associations', '-a', 3)
        self.assert_command('import_districts', '-d', 3)
        self.assert_command('setup', '-s', 2009, '-l', 9656, 9657, 10677)

        self.assert_command('import_games')


class SeasonStartTest(IntegrationTestCase):
    def test_first_hit(self):
        self.assert_command('import_associations', '-a', 80)
        self.assert_command('import_districts', '-d', 80)
        self.assert_command('setup', '-s', 2018, '-l', 34744)

        self.assert_objects(League, count=1)

    def test_first_hit_multiseason(self):
        self.assert_command('import_associations', '-a', 80)
        self.assert_command('import_districts', '-d', 80)
        self.assert_command('setup', '-s', 2017, 2018, '-l', 27265, 34744)

        self.assert_objects(League, count=2)

    def test_later_hit(self):
        self.assert_command('import_associations', '-a', 81)
        self.assert_command('import_districts', '-d', 81)
        self.assert_command('setup', '-s', 2018, '-l', 37511)

        self.assert_objects(League, count=1)

    def test_later_hit_multiseason(self):
        self.assert_command('import_associations', '-a', 81)
        self.assert_command('import_districts', '-d', 81)
        self.assert_command('setup', '-s', 2017, 2018, '-l', 30859, 37511)

        self.assert_objects(League, count=2)
