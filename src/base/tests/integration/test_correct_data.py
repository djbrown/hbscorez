from base.tests.base import IntegrationTestCase
from districts.models import District
from games.models import Game
from leagues.models import League, Season
from players.models import Score
from teams.models import Team


class ImportGamesTest(IntegrationTestCase):
    def test_specific_game(self):
        district = District.objects.create(bhv_id=1)
        season = Season.objects.create(start_year=2)
        league = League.objects.create(bhv_id=26773, district=district, season=season)
        team = Team.objects.create(bhv_id=3, league=league)
        Game.objects.create(number=210116, league=league, home_team=team, guest_team=team)

        self.assert_objects(Score, 0)

        self.assert_command("correct_data")

        self.assert_objects(Score, 26)

    def test_without_games(self):
        self.assert_objects(Score, 0)

        self.assert_command("correct_data")

        self.assert_objects(Score, 0)
