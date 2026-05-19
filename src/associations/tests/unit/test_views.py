from associations.models import Association
from base.tests.base import ViewTestCase
from clubs.models import Club
from districts.models import District


class TestViews(ViewTestCase):
    def test_list(self):
        a1 = Association.objects.create(name="Test Association 10", abbreviation="A10", bhv_id=10, source_url="")
        a2 = Association.objects.create(name="Test Association 20", abbreviation="A20", bhv_id=20, source_url="")
        response = self.get_url("associations:list")
        self.assertContains(response, a1.name)
        self.assertContains(response, a2.name)

    def test_list_empty(self):
        response = self.get_url("associations:list")
        self.assertEqual(response.status_code, 200)

    def test_detail(self):
        a = Association.objects.create(name="Test Association 10", abbreviation="A10", bhv_id=10, source_url="")
        response = self.get_url("associations:detail", pk=a.pk)
        self.assertContains(response, a.name)

    def test_detail_districts(self):
        a = Association.objects.create(name="Test Association 10", abbreviation="A10", bhv_id=10, source_url="")
        a.district_set.add(
            d1 := District.objects.create(name="Test District 101", bhv_id=101),
            d2 := District.objects.create(name="Test District 102", bhv_id=102),
        )
        response = self.get_url("associations:detail", pk=a.pk)
        self.assertContains(response, d1.name)
        self.assertContains(response, d2.name)

    def test_detail_clubs(self):
        a = Association.objects.create(name="Test Association 10", abbreviation="A10", bhv_id=10, source_url="")
        a.club_set.add(
            c1 := Club.objects.create(name="Test Club 101", bhv_id=101),
            c2 := Club.objects.create(name="Test Club 102", bhv_id=102),
        )
        response = self.get_url("associations:detail", pk=a.pk)
        self.assertContains(response, c1.name)
        self.assertContains(response, c2.name)

    def test_detail_not_found(self):
        response = self.get_url("associations:detail", pk=1)
        self.assertEqual(response.status_code, 404)
