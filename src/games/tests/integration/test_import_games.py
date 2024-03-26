import datetime
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from base import logic, parsing
from base.tests.base import IntegrationTestCase
from games.models import Game
from leagues.models import League, Season
from leagues.tests.integration import test_import_leagues
from players.models import Score
from sports_halls.models import SportsHall


class ImportGamesTest(IntegrationTestCase):

    def test_specific(self):
        self.assert_command('import_associations', '-a', 35)
        self.assert_command('import_districts', '-d', 35)
        self.assert_command('import_leagues', '-s', 2017, '-l', 26777)
        league = self.assert_objects(League)

        self.assert_command('import_games', '-g', 210226)
        game = self.assert_objects(Game)

        self.assertEqual(game.number, 210226)
        self.assertEqual(game.league, league)
        self.assertEqual(game.opening_whistle, timezone.make_aware(datetime.datetime(2017, 10, 7, 19, 45)))
        self.assertEqual(game.sports_hall.number, 22010)
        self.assertEqual(game.sports_hall.bhv_id, 487)
        self.assertEqual(game.home_team.short_name, 'TSVG Malsch')
        self.assertEqual(game.guest_team.short_name, 'HSG Dittig/TBB')
        self.assertEqual(game.home_goals, 24)
        self.assertEqual(game.guest_goals, 22)
        self.assertEqual(game.report_number, 490394)

    def test_mvl(self):
        self.assert_command('import_associations', '-a', 35)
        self.assert_command('import_districts', '-d', 35)
        self.assert_command('import_leagues', '-s', 2017, '-l', 26777)
        self.assert_objects(League)

        self.assert_command('import_games')
        self.assert_objects(Game, 182)

    def test_missing_sports_hall(self):
        self.assert_command('import_associations', '-a', 80)
        self.assert_command('import_districts', '-d', 80)
        self.assert_command('import_leagues', '-s', 2023, '-l', 109051)
        self.assert_command('import_games', '-g', 21000112)
        self.assert_objects(Game)

    def test_missing_district(self):
        self.assert_command('import_games', '-a', 35, '-d', 0)
        self.assert_objects(Game, 0)

    def test_multiseason(self):
        self.assert_command('import_associations', '-a', 35)
        self.assert_command('import_districts', '-d', 35)
        self.assert_command('import_leagues', '-s', 2017, 2018, '-l', 26777, 34606)
        self.assert_objects(Season, count=2)
        leagues = self.assert_objects(League, count=2)

        self.assert_command('import_games')

        for league in leagues:
            self.assertGreater(league.game_set.count(), 0, msg=f"league without games: {league}")


def read_html(file_name):
    file: Path = settings.ROOT_DIR / 'src' / 'games' / 'tests' / file_name
    content = file.read_text()
    return parsing.html_dom(content)


class UpdateTest(IntegrationTestCase):
    def test_update_game(self):
        self.assert_command('import_associations', '-a', 35)
        self.assert_command('import_districts', '-d', 35)
        self.assert_command('import_leagues', '-s', 2017, '-l', 26777)
        league = self.assert_objects(League)

        self.assert_command('import_games', '-g', 210226)
        self.assert_command('import_reports')
        self.assert_objects(Game)
        self.assert_objects(Score, count=27)

        dom = read_html('game_table_single_game.html')
        [game_row] = parsing.parse_game_rows(dom)
        sports_hall = SportsHall.objects.create(
            number=1, name="My Gym", address="addr", phone_number="tel", latitude="10", longitude="20", bhv_id=3)

        logic.scrape_game(game_row, league, sports_hall)

        game = self.assert_objects(Game)

        self.assertEqual(game.opening_whistle, timezone.make_aware(datetime.datetime(2017, 10, 8, 15, 0)))
        self.assertEqual(game.home_goals, 124)
        self.assertEqual(game.guest_goals, 122)
        self.assertEqual(game.report_number, 0)
        self.assertEqual(game.sports_hall, sports_hall)
        self.assertEqual(game.score_set.count(), 0)


class ForfeitTest(IntegrationTestCase):
    def test_forfeit_with_report(self):
        self.assert_command('import_associations', '-a', 3)
        self.assert_command('import_districts', '-d', 10)
        self.assert_command('import_leagues', '-s', 2018, '-l', 35537)

        self.assert_command('import_games', '-g', 60201)

        game: Game = self.assert_objects(Game)
        self.assertEqual(game.number, 60201)
        self.assertEqual(game.report_number, 710203)
        self.assertEqual(game.home_goals, 0)
        self.assertEqual(game.guest_goals, 0)
        self.assertEqual(game.forfeiting_team, game.guest_team)

    def test_forfeit_without_report(self):
        self.assert_command('import_associations', '-a', 35)
        self.assert_command('import_districts', '-d', 35)
        self.assert_command('import_leagues', '-s', 2018, '-l', 34606)

        self.assert_command('import_games', '-g', 210348)

        game: Game = self.assert_objects(Game)
        self.assertEqual(game.number, 210348)
        self.assertEqual(game.report_number, None)
        self.assertEqual(game.home_goals, 0)
        self.assertEqual(game.guest_goals, 0)
        self.assertEqual(game.forfeiting_team, game.guest_team)


class YouthTest(IntegrationTestCase):
    def test_youth(self):
        test_import_leagues.YouthTest.test_youth(self)

        self.assert_command('import_games', '--youth')

        league: League = self.assert_objects(League)
        self.assertGreater(league.game_set.count(), 0)

    def test_no_youth(self):
        test_import_leagues.YouthTest.test_youth(self)

        self.assert_command('import_games')

        self.assert_objects(Game, count=0)


class BuggedGameRowsTest(IntegrationTestCase):
    def test_additional_heading_row(self):
        self.assert_command('import_associations', '-a', 3)
        self.assert_command('import_districts', '-d', 8)
        self.assert_command('import_leagues', '-s', 2019, '-l', 46786)
        self.assert_command('import_games', '-g', 41013)
        self.assert_objects(Game)

    def test_additional_title(self):
        self.assert_command('import_associations', '-a', 78)
        self.assert_command('import_districts', '-d', 151)
        self.assert_command('import_leagues', '-s', 2023, '-l', 110541)
        self.assert_command('import_games')
        self.assert_objects(Game, count=3)

    def test_missing_sports_hall(self):
        self.assert_command('import_associations', '-a', 79)
        self.assert_command('import_districts', '-d', 79)
        self.assert_command('import_leagues', '-s', 2023, '-l', 102551)
        self.assert_command('import_games')
        self.assert_objects(SportsHall, count=0)
        self.assert_objects(Game, count=6)
