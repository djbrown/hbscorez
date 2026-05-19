from base.tests.base import ViewTestCase
from clubs.models import Club
from districts.models import District
from leagues.models import League, Season
from teams.models import Team


class TestViews(ViewTestCase):
    def test_detail(self):
        club = Club.objects.create(name="Test Club 10", bhv_id=10)
        district = District.objects.create(name="Test District 110", bhv_id=110)

        s25 = Season.objects.create(start_year=2025)
        l25 = League.objects.create(name="Test League 25", abbreviation="L25", bhv_id=25, district=district, season=s25)
        t25 = Team.objects.create(name="Test Team 251", short_name="T251", bhv_id=251, club=club, league=l25)

        s26 = Season.objects.create(start_year=2026)
        l26 = League.objects.create(name="Test League 26", abbreviation="L26", bhv_id=26, district=district, season=s26)
        t26 = Team.objects.create(name="Test Team 261", short_name="T261", bhv_id=261, club=club, league=l26)

        response = self.get_url("clubs:detail", pk=club.pk)
        self.assertContains(response, club.name)
        self.assertContains(response, s25.start_year)
        self.assertContains(response, t25.name)
        self.assertContains(response, l25.abbreviation)
        self.assertContains(response, s26.start_year)
        self.assertContains(response, t26.name)
        self.assertContains(response, l26.abbreviation)

    def test_detail_empty(self):
        club = Club.objects.create(name="Test Club 10", bhv_id=10)
        response = self.get_url("clubs:detail", pk=club.pk)
        self.assertContains(response, club.name)

    def test_detail_not_found(self):
        response = self.get_url("clubs:detail", pk=1)
        self.assertEqual(response.status_code, 404)
