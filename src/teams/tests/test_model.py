from django.test import TestCase

from teams.models import Team


class ShortName(TestCase):

    def test_two_to_one(self):
        name = 'irrelevant'
        short_names = ['two', 'one', 'two']

        actual = Team.find_matching_short_name(name, short_names)

        self.assertEqual('two', actual)

    def test_six_to_two(self):
        name = 'irrelevant'
        short_names = ['two', 'six', 'six', 'six', 'six', 'six', 'six',  'two']

        actual = Team.find_matching_short_name(name, short_names)

        self.assertEqual('six', actual)

    def test_three_options_max_count(self):
        name = 'irrelevant'
        short_names = ['four', 'one', 'four', 'two', 'three', 'four']

        actual = Team.find_matching_short_name(name, short_names)

        self.assertEqual('four', actual)

    def test_same_count_depend_on_name(self):
        name = 'TSV Zwei'
        short_names = ['eins', 'zwei', 'zwei', 'eins']

        actual = Team.find_matching_short_name(name, short_names)

        self.assertEqual('zwei', actual)
