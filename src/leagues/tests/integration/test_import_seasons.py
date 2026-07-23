from base.tests.base import IntegrationTestCase
from leagues.models import Season


class CommandTest(IntegrationTestCase):
    def test_specific_season(self):
        self.assert_command("import_seasons", "-s", 2017)

        season = self.assert_object(Season)
        self.assertEqual(season.start_year, 2017)

    def test_all_existing_seasons(self):
        self.assert_command("import_seasons")

        for start_year in range(2017, 2026):
            exists = Season.objects.filter(start_year=start_year).exists()
            self.assertTrue(exists, f"Season {start_year} should exist")

    def test_nonexisting_seasons(self):
        self.assert_command("import_seasons")

        for start_year in range(1999, 2004):
            exists = Season.objects.filter(start_year=start_year).exists()
            self.assertFalse(exists, f"Season {start_year} should not exist")
