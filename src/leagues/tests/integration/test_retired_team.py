import os
import unittest
from datetime import date

from django.conf import settings
from django.test import TestCase
from lxml import html

from base.parsing import parse_retirements
from base.tests.base import IntegrationTestCase
from leagues.models import League
from players.models import Score
from teams.models import Team


def read_html(file):
    path = os.path.join(settings.SRC_DIR, 'leagues', 'tests', file)
    with open(path, 'r') as report_file:
        content = report_file.read()
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


class RetiredTeamTest(IntegrationTestCase):
    def test_retired_team(self):
        self.assert_command('setup', '-a', 3, '-d', 4, '-s', 2018, '-l', 35068)
        self.assert_command('import_games')
        self.assert_objects(Team, 16)

        retirement = date(2018, 6, 29)
        retired_team = self.assert_objects(Team, filters={'retirement': retirement})
        self.assertEqual(retired_team.name, 'TV 1893 Neuhausen/E.')

    def test_another_retired_team(self):
        self.assert_command('setup', '-a', 3, '-d', 7, '-s', 2017, '-l', 28454)
        self.assert_command('import_games')
        self.assert_objects(Team, 5)

        retirement = date(2018, 3, 1)
        retired_team = self.assert_objects(Team, filters={'retirement': retirement})
        self.assertEqual(retired_team.name, 'TSG Stuttgart')

    def test_retirement_during_season(self):
        self.assert_command('setup', '-a', 3, '-d', 7, '-s', 2017, '-l', 28454)
        team = self.assert_objects(Team, filters={'retirement__isnull': False})
        team.retirement = None
        team.save()
        self.assert_command('import_games', '-g', '30901')
        self.assert_command('import_reports')
        other_teams_scores_count_before = Score.objects.exclude(player__team=team).count()

        self.assertGreater(team.player_set.count(), 0)
        self.assertGreater(Score.objects.filter(player__team=team).count(), 0)

        self.assert_command('setup', '-a', 3, '-d', 7, '-s', 2017, '-l', 28454)
        self.assert_command('import_reports')
        team = self.assert_objects(Team, filters={'retirement__isnull': False})
        other_teams_scores_count_after = Score.objects.exclude(player__team=team).count()

        self.assertGreater(team.player_set.count(), 0)
        self.assertEqual(Score.objects.filter(player__team=team).count(), 0)
        self.assertGreater(other_teams_scores_count_before, other_teams_scores_count_after)

    def test_nonexisting_retired_team(self):
        self.assert_command('setup', '-a', 3, '-d', 7, '-s', 2019, '-l', 48708)
        self.assert_objects(League)
