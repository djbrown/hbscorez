from base.tests.base import ViewTestCase
from districts.models import District
from leagues.models import League, Season


class TestViews(ViewTestCase):
    def test_detail(self):
        district = District.objects.create(name="Test District 10", bhv_id=10)
        s25 = Season.objects.create(start_year=2025)
        l25 = League.objects.create(name="Test League 25", abbreviation="L25", bhv_id=25, district=district, season=s25)
        s26 = Season.objects.create(start_year=2026)
        l26 = League.objects.create(name="Test League 26", abbreviation="L26", bhv_id=26, district=district, season=s26)

        response = self.get_url("districts:detail", pk=district.pk)
        self.assertContains(response, district.name)
        self.assertContains(response, s25.start_year)
        self.assertContains(response, l25.name)
        self.assertContains(response, s26.start_year)
        self.assertContains(response, l26.name)

    def test_detail_empty(self):
        district = District.objects.create(name="Test District 10", bhv_id=10)
        response = self.get_url("districts:detail", pk=district.pk)
        self.assertContains(response, district.name)

    def test_detail_not_found(self):
        response = self.get_url("districts:detail", pk=1)
        self.assertEqual(response.status_code, 404)
