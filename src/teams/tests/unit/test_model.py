from django.test import TestCase

from base.tests.base import ModelTestCase
from districts.models import District
from leagues.models import League, Season
from teams.models import Team


class RenamedTeam(ModelTestCase):
    def test_renamed_team(self):
        district = District.objects.create(bhv_id=4)
        season = Season.objects.create(start_year=2018)
        league = League.objects.create(
            name="League 23",
            abbreviation="L23",
            bhv_id=23,
            district=district,
            season=season,
        )

        Team.objects.create(name="Team 1", short_name="T 1", league=league, bhv_id=1)

        Team.create_or_update_team(name="Team Eins", short_name="Team E", league=league, club=None, bhv_id=1)

        self.assert_object(Team, filters={"name": "Team Eins", "short_name": "Team E"})


class ShortName(TestCase):

    def test_two_to_one(self):
        name = "irrelevant"
        short_names = ["two", "one", "two"]

        actual = Team.find_matching_short_name(name, short_names)

        self.assertEqual("two", actual)

    def test_six_to_two(self):
        name = "irrelevant"
        short_names = ["two", "six", "six", "six", "six", "six", "six", "two"]

        actual = Team.find_matching_short_name(name, short_names)

        self.assertEqual("six", actual)

    def test_three_options_max_count(self):
        name = "irrelevant"
        short_names = ["four", "one", "four", "two", "three", "four"]

        actual = Team.find_matching_short_name(name, short_names)

        self.assertEqual("four", actual)

    def test_same_count_depend_on_name(self):
        name = "TSV Zwei"
        short_names = ["eins", "zwei", "zwei", "eins"]

        actual = Team.find_matching_short_name(name, short_names)

        self.assertEqual("zwei", actual)

    def test_same_count_depend_on_name_other(self):
        name = "TSV Eins"
        short_names = ["eins", "zwei", "zwei", "eins"]

        actual = Team.find_matching_short_name(name, short_names)

        self.assertEqual("eins", actual)
