import unittest

from django.conf import settings

from associations.models import Association
from base.tests.base import IntegrationTestCase
from districts.models import District
from leagues.models import League, LeagueName, Season


class CommandTest(IntegrationTestCase):
    def test_specific(self):
        a = Association.objects.create(bhv_id=95, source_url=f"{settings.NEW_ROOT_SOURCE_URL}/home/portal/luxemburg")
        District.objects.create(bhv_id=95).associations.add(a)
        Season.objects.create(start_year=2024, bhv_id=130)

        self.assert_command("import_leagues", "-l", 127086)

        league = self.assert_object(League)
        self.assertEqual(league.name, "AXA League Männer")
        self.assertEqual(league.abbreviation, "H-AXA")
        self.assertEqual(league.bhv_id, 127086)

    def test_update(self):
        a = Association.objects.create(bhv_id=95, source_url=f"{settings.NEW_ROOT_SOURCE_URL}/home/portal/luxemburg")
        district = District.objects.create(bhv_id=95)
        district.associations.add(a)
        season = Season.objects.create(start_year=2024, bhv_id=130)
        League.objects.create(name="My League", abbreviation="ABBR", district=district, season=season, bhv_id=127086)

        self.assert_command("import_leagues", "-l", 127086)

        league = self.assert_object(League)
        self.assertEqual(league.name, "AXA League Männer")
        self.assertEqual(league.abbreviation, "H-AXA")
        self.assertEqual(league.bhv_id, 127086)

    def test_multiseason(self):
        a = Association.objects.create(bhv_id=95, source_url=f"{settings.NEW_ROOT_SOURCE_URL}/home/portal/luxemburg")
        District.objects.create(bhv_id=95).associations.add(a)
        Season.objects.create(start_year=2023, bhv_id=121)
        Season.objects.create(start_year=2024, bhv_id=130)

        self.assert_command("import_leagues", "-s", 2023, 2024, "-l", 111316, 127086)

        self.assert_objects(League, count=2)

    def test_without_association_filter(self):
        a = Association.objects.create(bhv_id=95, source_url=f"{settings.NEW_ROOT_SOURCE_URL}/home/portal/luxemburg")
        District.objects.create(bhv_id=95).associations.add(a)
        Season.objects.create(start_year=2024, bhv_id=130)

        self.assert_command("import_leagues", "-s", 2024, "-l", 127086)

        self.assert_object(League)

    def test_season_filter(self):
        a = Association.objects.create(bhv_id=95, source_url=f"{settings.NEW_ROOT_SOURCE_URL}/home/portal/luxemburg")
        District.objects.create(bhv_id=95).associations.add(a)
        Season.objects.create(start_year=2023, bhv_id=121)
        Season.objects.create(start_year=2024, bhv_id=130)

        self.assert_command("import_leagues", "-s", 2024, "-l", 111316, 127086)

        self.assert_object(League)

    def test_all(self):
        self.assert_command("import_associations")
        self.assert_command("import_districts")
        self.assert_command("import_seasons")
        self.assert_command("import_leagues")

        self.assert_objects(League, 25)


@unittest.skip("broken integration test")
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


@unittest.skip("broken integration test")
class FewGames(IntegrationTestCase):
    def test_short_name_single_game_per_team(self):
        LeagueName.objects.create(bhv_id=83521, name="608120 Aufstieg Männer KL")

        self.assert_command("import_associations", "-a", 78)
        self.assert_command("import_districts", "-d", 146)
        self.assert_command("import_leagues", "-s", 2021, "-l", 83521)

        self.assert_object(League)


@unittest.skip("broken integration test")
class YouthTest(IntegrationTestCase):
    def test_youth(self):
        self.assert_command("import_associations", "-a", 35)
        self.assert_command("import_districts", "-d", 35)
        self.assert_command("import_leagues", "-s", 2019, "-l", 46921, "--youth")

        league: League = self.assert_object(League)
        self.assertTrue(league.youth)

    def test_no_youth(self):
        self.assert_command("import_associations", "-a", 35)
        self.assert_command("import_districts", "-d", 35)
        self.assert_command("import_leagues", "-s", 2019, "-l", 46921)

        self.assert_objects(League, count=0)
