from base.tests.base import IntegrationTestCase
from districts.models import District
from leagues.models import League, LeagueName, Season


class SeasonTest(IntegrationTestCase):
    def test_specific(self):
        self.assert_command("import_associations", "-a", 35)
        self.assert_command("import_districts", "-d", 35)
        self.assert_command("import_leagues", "-s", 2017, "-l", 0)

        season = self.assert_objects(Season)
        self.assertEqual(season.start_year, 2017)

    def test_all(self):
        self.assert_command("import_associations", "-a", 4)
        self.assert_command("import_districts", "-d", 3)
        self.assert_command("import_leagues", "-l", 0)

        self.assert_objects(League, 0)
        for start_year in range(2004, 2023):
            exists = Season.objects.filter(start_year=start_year).exists()
            self.assertTrue(exists, f"Season {start_year} should exist")

    def test_old_seasons(self):
        self.assert_command("import_associations", "-a", 4)
        self.assert_command("import_districts", "-d", 3)
        self.assert_command("import_leagues", "-l", 0)

        self.assert_objects(League, count=0)

        for start_year in range(1999, 2004):
            exists = Season.objects.filter(start_year=start_year).exists()
            self.assertFalse(exists, f"Season {start_year} should not exist")


class SeasonStartTest(IntegrationTestCase):
    def test_first_hit(self):
        self.assert_command("import_associations", "-a", 80)
        self.assert_command("import_districts", "-d", 80)
        self.assert_command("import_leagues", "-s", 2018, "-l", 34744)

        self.assert_objects(League, count=1)

    def test_first_hit_multiseason(self):
        self.assert_command("import_associations", "-a", 80)
        self.assert_command("import_districts", "-d", 80)
        self.assert_command("import_leagues", "-s", 2017, 2018, "-l", 27265, 34744)

        self.assert_objects(League, count=2)

    def test_later_hit(self):
        self.assert_command("import_associations", "-a", 81)
        self.assert_command("import_districts", "-d", 81)
        self.assert_command("import_leagues", "-s", 2018, "-l", 37511)

        self.assert_objects(League, count=1)

    def test_later_hit_multiseason(self):
        self.assert_command("import_associations", "-a", 81)
        self.assert_command("import_districts", "-d", 81)
        self.assert_command("import_leagues", "-s", 2017, 2018, "-l", 30859, 37511)

        self.assert_objects(League, count=2)


class CommandTest(IntegrationTestCase):
    def test_specific(self):
        self.assert_command("import_associations", "-a", 35)
        self.assert_command("import_districts", "-d", 35)
        self.assert_command("import_leagues", "-s", 2017, "-l", 26777)

        league = self.assert_objects(League)
        self.assertEqual(league.name, "Verbandsliga Männer")
        self.assertEqual(league.abbreviation, "M-VL")
        self.assertEqual(league.bhv_id, 26777)

    def test_update(self):
        self.assert_command("import_associations", "-a", 35)
        self.assert_command("import_districts", "-d", 35)
        district = self.assert_objects(District)
        season = Season.objects.create(start_year=2017)
        League.objects.create(name="My League", abbreviation="ABBR", district=district, season=season, bhv_id=26777)

        self.assert_command("import_leagues", "-s", 2017, "-l", 26777)

        league = self.assert_objects(League)
        self.assertEqual(league.name, "Verbandsliga Männer")
        self.assertEqual(league.abbreviation, "M-VL")
        self.assertEqual(league.bhv_id, 26777)

    def test_oberliga_hamburg_schleswig(self):
        self.assert_command("import_associations", "-a", 77)
        self.assert_command("import_districts", "-d", 77)
        self.assert_command("import_leagues", "-s", 2021, "-l", 77606)
        self.assert_objects(League)


class SpecificLeagueTest(IntegrationTestCase):

    def test_mvl_2016(self):
        self.assert_command("import_associations", "-a", 35)
        self.assert_command("import_districts", "-d", 35)
        self.assert_command("import_leagues", "-s", 2016, "-l", 21666)

        season = self.assert_objects(Season)
        self.assertEqual(season.start_year, 2016)

        league = self.assert_objects(League)
        self.assertEqual(league.name, "Verbandsliga Männer")
        self.assertEqual(league.abbreviation, "M-VL")
        self.assertEqual(league.bhv_id, 21666)
        self.assertEqual(league.season, season)

    def test_mvl_2017(self):
        self.assert_command("import_associations", "-a", 35)
        self.assert_command("import_districts", "-d", 35)
        self.assert_command("import_leagues", "-s", 2017, "-l", 26777)

        season = self.assert_objects(Season)
        self.assertEqual(season.start_year, 2017)

        league = self.assert_objects(League)
        self.assertEqual(league.name, "Verbandsliga Männer")
        self.assertEqual(league.abbreviation, "M-VL")
        self.assertEqual(league.bhv_id, 26777)
        self.assertEqual(league.season, season)

    def test_mwls_2016(self):
        self.assert_command("import_associations", "-a", 3)
        self.assert_command("import_districts", "-d", 3)
        self.assert_command("import_leagues", "-s", 2016, "-l", 21747)

        season = self.assert_objects(Season)
        self.assertEqual(season.start_year, 2016)

        league = self.assert_objects(League)
        self.assertEqual(league.name, "Männer Württemberg-Liga Süd")
        self.assertEqual(league.abbreviation, "M-WL-S")
        self.assertEqual(league.bhv_id, 21747)
        self.assertEqual(league.season, season)

    def test_mwls_2017(self):
        self.assert_command("import_associations", "-a", 3)
        self.assert_command("import_districts", "-d", 3)
        self.assert_command("import_leagues", "-s", 2017, "-l", 27505)

        season = self.assert_objects(Season)
        self.assertEqual(season.start_year, 2017)

        league = self.assert_objects(League)
        self.assertEqual(league.name, "Männer Württemberg-Liga Süd")
        self.assertEqual(league.abbreviation, "M-WL-S")
        self.assertEqual(league.bhv_id, 27505)
        self.assertEqual(league.season, season)


class LeagueNameTest(IntegrationTestCase):
    def test_long_name(self):
        self.assert_command("import_associations", "-a", 83)
        self.assert_command("import_districts", "-d", 83)
        self.assert_command("import_leagues", "-s", 2019, "-l", 45646, 45651, "--youth")

        leagues = self.assert_objects(League, count=2).order_by("name")
        self.assertEqual(leagues[0].name, "männliche Jgd. B - Kreisklasse")
        self.assertEqual(leagues[1].name, "männliche Jgd. B - Rheinhessenliga")

    def test_ignored_name(self):
        LeagueName.objects.create(bhv_id=91991, name="EN-Turnier")

        self.assert_command("import_associations", "-a", 78)
        self.assert_command("import_districts", "-d", 161)
        self.assert_command("import_leagues", "-s", 2022, "-l", 91991)

        self.assert_objects(League, count=0)

    def test_pokal(self):
        self.assert_command("import_associations", "-a", 56)
        self.assert_command("import_districts", "-d", 62)
        self.assert_command("import_leagues", "-s", 2019, "-l", 45411)

        self.assert_objects(League, count=0)

    def test_meisterschaft(self):
        self.assert_command("import_associations", "-a", 3)
        self.assert_command("import_districts", "-d", 3)
        self.assert_command("import_leagues", "-s", 2009, "-l", 9656, 9657, 10677)

        self.assert_command("import_games")

    def test_mklc2_2007(self):
        LeagueName.objects.create(bhv_id=7424, name="Männer Kreisliga C Staffel 3")

        self.assert_command("import_associations", "-a", 3)
        self.assert_command("import_districts", "-d", 7)
        self.assert_command("import_leagues", "-s", 2007, "-l", 7423, 7424)

        self.assert_objects(League, count=2)
        mklc2 = League.objects.get(abbreviation="M-KLC-2")
        mklc3 = League.objects.get(abbreviation="M-KLC-3")

        self.assertEqual(mklc2.name, "Männer Kreisliga C Staffel 2")
        self.assertEqual(mklc3.name, "Männer Kreisliga C Staffel 3")

    def test_mkl2_2005(self):
        LeagueName.objects.create(bhv_id=5380, name="Männer Kreisliga 2-1")
        LeagueName.objects.create(bhv_id=5381, name="Männer Kreisliga 2-2")

        self.assert_command("import_associations", "-a", 3)
        self.assert_command("import_districts", "-d", 10)
        self.assert_command("import_leagues", "-s", 2005, "-l", 5380, 5381)

        self.assert_objects(League, count=2)
        mkl21 = League.objects.get(abbreviation="M-KL2-1")
        mkl22 = League.objects.get(abbreviation="M-KL2-2")

        self.assertEqual(mkl21.name, "Männer Kreisliga 2-1")
        self.assertEqual(mkl22.name, "Männer Kreisliga 2-2")


class FewGames(IntegrationTestCase):
    def test_short_name_single_game_per_team(self):
        LeagueName.objects.create(bhv_id=83521, name="608120 Aufstieg Männer KL")

        self.assert_command("import_associations", "-a", 78)
        self.assert_command("import_districts", "-d", 146)
        self.assert_command("import_leagues", "-s", 2021, "-l", 83521)

        self.assert_objects(League)


class YouthTest(IntegrationTestCase):
    def test_youth(self):
        self.assert_command("import_associations", "-a", 35)
        self.assert_command("import_districts", "-d", 35)
        self.assert_command("import_leagues", "-s", 2019, "-l", 46921, "--youth")

        league: League = self.assert_objects(League)
        self.assertTrue(league.youth)

    def test_no_youth(self):
        self.assert_command("import_associations", "-a", 35)
        self.assert_command("import_districts", "-d", 35)
        self.assert_command("import_leagues", "-s", 2019, "-l", 46921)

        self.assert_objects(League, count=0)
