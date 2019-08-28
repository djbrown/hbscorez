import os
from datetime import date

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from lxml import html

from base.parsing import parse_retirements
from base.tests.model_test_case import ModelTestCase
from teams.models import Team


def read_html(file):
    path = os.path.join(settings.SRC_DIR, 'leagues', 'tests', file)
    with open(path, 'r') as f:
        content = f.read()
    return html.fromstring(content)


class ParseRetiredTeamTest(TestCase):
    def test_empty_retirement(self):
        dom = read_html('league_without_retired_team.html')
        retirements = parse_retirements(dom)
        self.assertEqual(retirements, [])

    def test_retired_team(self):
        dom = read_html('league_with_retired_team.html')
        retirements = parse_retirements(dom)
        expected = [('TV 1893 Neuhausen/E.', date(2018, 6, 29))]
        self.assertEqual(expected, retirements)

    def test_another_retired_team(self):
        dom = read_html('league_with_retired_team_28454.html')
        retirements = parse_retirements(dom)
        expected = [('TSG Stuttgart', date(2018, 3, 1))]
        self.assertEqual(expected, retirements)


class RetiredTeamTest(ModelTestCase):
    def test_reired_team(self):
        call_command('setup', '-a', 3, '-d', 4, '-s', 2018, '-l', 35068)
        call_command('import_games')
        self.assert_objects(Team, 16)

        retirement = date(2018, 6, 29)
        retired_team = self.assert_objects(Team, filters={'retirement': retirement})
        self.assertEqual(retired_team.name, 'TV 1893 Neuhausen/E.')

    def test_another_reired_team(self):
        call_command('setup', '-a', 3, '-d', 7, '-s', 2017, '-l', 28454)
        call_command('import_games')
        self.assert_objects(Team, 5)

        retirement = date(2018, 3, 1)
        retired_team = self.assert_objects(Team, filters={'retirement': retirement})
        self.assertEqual(retired_team.name, 'TSG Stuttgart')
