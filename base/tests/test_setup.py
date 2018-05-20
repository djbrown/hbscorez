from django.core.management import call_command
from django.test import TestCase

from base import models


class ParseReportNumberTest(TestCase):

    def assert_single_object(self, model):
        objects = model.objects.all()
        self.assertTrue(objects.exists())
        self.assertEqual(len(objects), 1)
        return objects[0]

    def test__setup__association(self):
        return_code = call_command('setup', '-a 35', '-d 0')
        self.assertEqual(return_code, None)
        association = self.assert_single_object(models.Association)
        self.assertEqual(association.bhv_id, 35)
        self.assertEqual(association.name, "Badischer Handball-Verband")

    def test__setup__district(self):
        return_code = call_command('setup', '-a 35', '-d 35', '-l 0')
        self.assertEqual(return_code, None)
        district = self.assert_single_object(models.District)
        self.assertEqual(district.bhv_id, 35)
        self.assertEqual(district.name, "BHV-Ligen")

    def test__setup__league(self):
        return_code = call_command('setup', '-a 35', '-d 35', '-l 26777')
        self.assertEqual(return_code, None)

        league = self.assert_single_object(models.League)
        self.assertEqual(league.name, "Verbandsliga Männer")
        self.assertEqual(league.abbreviation, "M-VL")

        season = self.assert_single_object(models.Season)
        self.assertEqual(season.year, 2017)

        league_season = self.assert_single_object(models.LeagueSeason)
        self.assertEqual(league_season.bhv_id, 26777)
