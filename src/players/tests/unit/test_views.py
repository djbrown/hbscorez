from base.tests.base import ViewTestCase
from districts.models import District
from games.models import Game
from leagues.models import League, Season
from players.models import Player, Score
from teams.models import Team


class TestViews(ViewTestCase):
    def test_detail(self):
        district = District.objects.create(name="Test District 10", bhv_id=10)
        season = Season.objects.create(start_year=2025)
        lg = League.objects.create(name="Test L 25", abbreviation="L25", bhv_id=25, district=district, season=season)
        team = Team.objects.create(name="Test Team 251", short_name="T251", bhv_id=251, league=lg)
        player = Player.objects.create(name="Test Player 2511", team=team)
        game = Game.objects.create(number=2501, league=lg, home_team=team, guest_team=team, report_number=123456)
        score = Score.objects.create(player=player, player_number=77, game=game, goals=18)

        response = self.get_url("players:detail", pk=player.pk)
        self.assertContains(response, player.name)
        self.assertContains(response, team.short_name)
        self.assertContains(response, score.player_number)
        self.assertContains(response, score.goals)
        self.assertContains(response, game.report_number)

    def test_empty(self):
        district = District.objects.create(name="Test District 10", bhv_id=10)
        season = Season.objects.create(start_year=2025)
        lg = League.objects.create(name="Test L 25", abbreviation="L25", bhv_id=25, district=district, season=season)
        team = Team.objects.create(name="Test Team 251", short_name="T251", bhv_id=251, league=lg)
        player = Player.objects.create(name="Test Player 2511", team=team)
        response = self.get_url("players:detail", pk=lg.pk)
        self.assertContains(response, player.name)

    def test_not_found(self):
        response = self.get_url("players:detail", pk=1)
        self.assertEqual(response.status_code, 404)
