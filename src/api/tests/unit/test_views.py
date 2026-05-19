from associations.models import Association
from base.tests.base import ViewTestCase
from districts.models import District
from leagues.models import League, Season
from teams.models import Team


class TestAssociations(ViewTestCase):
    def test(self):
        a10 = Association.objects.create(name="Test Association 10", abbreviation="A10", bhv_id=10, source_url="")
        a20 = Association.objects.create(name="Test Association 20", abbreviation="A20", bhv_id=20, source_url="")
        response = self.get_url("api:associations")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "associations": [
                    {"pk": a10.pk, "name": a10.name, "abbreviation": a10.abbreviation},
                    {"pk": a20.pk, "name": a20.name, "abbreviation": a20.abbreviation},
                ]
            },
        )

    def test_empty(self):
        response = self.get_url("api:associations")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"associations": []})


class TestAssociationDistricts(ViewTestCase):
    def test(self):
        a = Association.objects.create(name="Test Association 10", abbreviation="A10", bhv_id=10, source_url="")
        a.district_set.add(
            d1 := District.objects.create(name="Test District 101", bhv_id=101),
            d2 := District.objects.create(name="Test District 102", bhv_id=102),
        )
        response = self.get_url("api:association_districts", pk=a.pk)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"districts": [{"pk": d1.pk, "name": d1.name}, {"pk": d2.pk, "name": d2.name}]},
        )

    def test_empty(self):
        a = Association.objects.create(name="Test Association 10", abbreviation="A10", bhv_id=10, source_url="")
        response = self.get_url("api:association_districts", pk=a.pk)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"districts": []})

    def test_association_not_found(self):
        response = self.get_url("api:association_districts", pk=1)
        self.assertContains(response, "No matching Association found.", status_code=404)


class TestSeasons(ViewTestCase):
    def test(self):
        season = Season.objects.create(start_year=2026)
        response = self.get_url("api:seasons")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"seasons": [{"startYear": season.start_year}]})

    def test_empty(self):
        response = self.get_url("api:seasons")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"seasons": []})


class TestDistrictSeasonLeagues(ViewTestCase):
    def test(self):
        district = District.objects.create(name="Test District 10", bhv_id=10)
        season = Season.objects.create(start_year=2026)
        l1 = League.objects.create(name="Test L 11", abbreviation="L11", district=district, season=season, bhv_id=11)
        l2 = League.objects.create(name="Test L 12", abbreviation="L12", district=district, season=season, bhv_id=12)
        response = self.get_url("api:district_season_leagues", pk=district.pk, start_year=season.start_year)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"leagues": [{"pk": l1.pk, "name": l1.name}, {"pk": l2.pk, "name": l2.name}]},
        )

    def test_empty(self):
        district = District.objects.create(name="Test District 10", bhv_id=10)
        season = Season.objects.create(start_year=2026)
        response = self.get_url("api:district_season_leagues", pk=district.pk, start_year=season.start_year)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"leagues": []})

    def test_district_not_found(self):
        season = Season.objects.create(start_year=2026)
        response = self.get_url("api:district_season_leagues", pk=1, start_year=season.start_year)
        self.assertContains(response, "No matching District found.", status_code=404)

    def test_season_not_found(self):
        district = District.objects.create(name="Test District 10", bhv_id=10)
        response = self.get_url("api:district_season_leagues", pk=district.pk, start_year=2026)
        self.assertContains(response, "No matching Season found.", status_code=404)


class TestLeagueTeams(ViewTestCase):
    def test(self):
        district = District.objects.create(name="Test District 10", bhv_id=10)
        season = Season.objects.create(start_year=2026)
        lg = League.objects.create(name="Test L 20", abbreviation="L20", bhv_id=20, district=district, season=season)
        t1 = Team.objects.create(name="Test Team 21", short_name="T21", bhv_id=21, league=lg)
        t2 = Team.objects.create(name="Test Team 22", short_name="T22", bhv_id=22, league=lg)
        response = self.get_url("api:league_teams", pk=lg.pk)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "teams": [
                    {"pk": t1.pk, "name": t1.name, "shortName": t1.short_name},
                    {"pk": t2.pk, "name": t2.name, "shortName": t2.short_name},
                ]
            },
        )

    def test_empty(self):
        district = District.objects.create(name="Test District 10", bhv_id=10)
        season = Season.objects.create(start_year=2026)
        lg = League.objects.create(name="Test L 11", abbreviation="L11", district=district, season=season, bhv_id=11)
        response = self.get_url("api:league_teams", pk=lg.pk)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"teams": []})

    def test_not_found(self):
        response = self.get_url("api:league_teams", pk=1)
        self.assertContains(response, "No matching League found.", status_code=404)
