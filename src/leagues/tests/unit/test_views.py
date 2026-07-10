from datetime import timedelta

from associations.models import Association
from base.tests.base import ViewTestCase
from districts.models import District
from games.models import Game
from leagues.models import League, Season
from players.models import Player, Score
from sports_halls.models import SportsHall
from teams.models import Team


class TestDetails(ViewTestCase):
    def test(self):
        association = Association.objects.create(name="Test Association 1", abbreviation="A1", bhv_id=1, source_url="")
        district = District.objects.create(name="Test District 10", bhv_id=10)
        district.associations.add(association)
        season = Season.objects.create(start_year=2025)
        lg = League.objects.create(name="Test L 25", abbreviation="L25", bhv_id=25, district=district, season=season)
        team = Team.objects.create(name="Test Team 251", short_name="T251", bhv_id=251, league=lg)
        scorer = Player.objects.create(name="Test Player 2511", team=team)
        offender = Player.objects.create(name="Test Player 2512", team=team)
        game = Game.objects.create(number=2501, league=lg, home_team=team, guest_team=team)
        Score.objects.create(player=scorer, player_number=6, game=game, goals=8)
        Score.objects.create(player=offender, player_number=3, game=game, warning_time=timedelta(minutes=7))

        response = self.get_url("leagues:detail", pk=lg.pk)
        self.assertContains(response, lg.name)
        self.assertContains(response, lg.abbreviation)
        self.assertContains(response, team.name)
        self.assertContains(response, scorer.name)
        self.assertContains(response, offender.name)

    def test_empty(self):
        association = Association.objects.create(name="Test Association 1", abbreviation="A1", bhv_id=1, source_url="")
        district = District.objects.create(name="Test District 10", bhv_id=10)
        district.associations.add(association)
        season = Season.objects.create(start_year=2025)
        lg = League.objects.create(name="Test L 25", abbreviation="L25", bhv_id=25, district=district, season=season)
        response = self.get_url("leagues:detail", pk=lg.pk)
        self.assertContains(response, lg.name)
        self.assertContains(response, lg.abbreviation)

    def test_not_found(self):
        response = self.get_url("leagues:detail", pk=1)
        self.assertEqual(response.status_code, 404)


class TestTeams(ViewTestCase):
    def test(self):
        association = Association.objects.create(name="Test Association 1", abbreviation="A1", bhv_id=1, source_url="")
        district = District.objects.create(name="Test District 10", bhv_id=10)
        district.associations.add(association)
        season = Season.objects.create(start_year=2025)
        lg = League.objects.create(name="Test L 25", abbreviation="L25", bhv_id=25, district=district, season=season)
        team251 = Team.objects.create(name="Test Team 251", short_name="T251", bhv_id=251, league=lg)
        team252 = Team.objects.create(name="Test Team 252", short_name="T252", bhv_id=252, league=lg)

        response = self.get_url("leagues:teams", pk=lg.pk)
        self.assertContains(response, lg.name)
        self.assertContains(response, lg.abbreviation)
        self.assertContains(response, team251.name)
        self.assertContains(response, team252.name)

    def test_empty(self):
        association = Association.objects.create(name="Test Association 1", abbreviation="A1", bhv_id=1, source_url="")
        district = District.objects.create(name="Test District 10", bhv_id=10)
        district.associations.add(association)
        season = Season.objects.create(start_year=2025)
        lg = League.objects.create(name="Test L 25", abbreviation="L25", bhv_id=25, district=district, season=season)
        response = self.get_url("leagues:teams", pk=lg.pk)
        self.assertContains(response, lg.name)
        self.assertContains(response, lg.abbreviation)

    def test_not_found(self):
        response = self.get_url("leagues:teams", pk=1)
        self.assertEqual(response.status_code, 404)


class TestGames(ViewTestCase):
    def test(self):
        association = Association.objects.create(name="Test Association 1", abbreviation="A1", bhv_id=1, source_url="")
        district = District.objects.create(name="Test District 10", bhv_id=10)
        district.associations.add(association)
        season = Season.objects.create(start_year=2025)
        lg = League.objects.create(name="Test L 25", abbreviation="L25", bhv_id=25, district=district, season=season)
        team = Team.objects.create(name="Test Team 251", short_name="T251", bhv_id=251, league=lg)
        sports_hall = SportsHall.objects.create(number=3, name="Test Sports Hall 3", address="Test Adr 3", bhv_id=30)
        game = Game.objects.create(
            number=2501, league=lg, home_team=team, guest_team=team, report_number=2036, sports_hall=sports_hall
        )

        response = self.get_url("leagues:games", pk=lg.pk)
        self.assertContains(response, lg.name)
        self.assertContains(response, lg.abbreviation)
        self.assertContains(response, team.short_name)
        self.assertContains(response, sports_hall.name)
        self.assertContains(response, game.report_number)

    def test_empty(self):
        association = Association.objects.create(name="Test Association 1", abbreviation="A1", bhv_id=1, source_url="")
        district = District.objects.create(name="Test District 10", bhv_id=10)
        district.associations.add(association)
        season = Season.objects.create(start_year=2025)
        lg = League.objects.create(name="Test L 25", abbreviation="L25", bhv_id=25, district=district, season=season)
        response = self.get_url("leagues:games", pk=lg.pk)
        self.assertContains(response, lg.name)
        self.assertContains(response, lg.abbreviation)

    def test_not_found(self):
        response = self.get_url("leagues:games", pk=1)
        self.assertEqual(response.status_code, 404)


class TestScorers(ViewTestCase):
    def test(self):
        association = Association.objects.create(name="Test Association 1", abbreviation="A1", bhv_id=1, source_url="")
        district = District.objects.create(name="Test District 10", bhv_id=10)
        district.associations.add(association)
        season = Season.objects.create(start_year=2025)
        lg = League.objects.create(name="Test L 25", abbreviation="L25", bhv_id=25, district=district, season=season)
        team = Team.objects.create(name="Test Team 251", short_name="T251", bhv_id=251, league=lg)
        scorer = Player.objects.create(name="Test Player 2511", team=team)
        game = Game.objects.create(number=2501, league=lg, home_team=team, guest_team=team)
        Score.objects.create(player=scorer, player_number=6, game=game, goals=8)

        response = self.get_url("leagues:scorers", pk=lg.pk)
        self.assertContains(response, lg.name)
        self.assertContains(response, lg.abbreviation)
        self.assertContains(response, team.short_name)
        self.assertContains(response, scorer.name)

    def test_empty(self):
        association = Association.objects.create(name="Test Association 1", abbreviation="A1", bhv_id=1, source_url="")
        district = District.objects.create(name="Test District 10", bhv_id=10)
        district.associations.add(association)
        season = Season.objects.create(start_year=2025)
        lg = League.objects.create(name="Test L 25", abbreviation="L25", bhv_id=25, district=district, season=season)
        team = Team.objects.create(name="Test Team 251", short_name="T251", bhv_id=251, league=lg)
        goalless = Player.objects.create(name="Test Player 2511", team=team)
        game = Game.objects.create(number=2501, league=lg, home_team=team, guest_team=team)
        Score.objects.create(player=goalless, player_number=3, game=game, warning_time=timedelta(minutes=7))
        response = self.get_url("leagues:scorers", pk=lg.pk)
        self.assertNotContains(response, goalless.name)

    def test_not_found(self):
        response = self.get_url("leagues:scorers", pk=1)
        self.assertEqual(response.status_code, 404)


class TestOffenders(ViewTestCase):
    def test(self):
        association = Association.objects.create(name="Test Association 1", abbreviation="A1", bhv_id=1, source_url="")
        district = District.objects.create(name="Test District 10", bhv_id=10)
        district.associations.add(association)
        season = Season.objects.create(start_year=2025)
        lg = League.objects.create(name="Test L 25", abbreviation="L25", bhv_id=25, district=district, season=season)
        team = Team.objects.create(name="Test Team 251", short_name="T251", bhv_id=251, league=lg)
        offender = Player.objects.create(name="Test Offender 2511", team=team)
        game = Game.objects.create(number=2501, league=lg, home_team=team, guest_team=team)
        Score.objects.create(player=offender, player_number=6, game=game, warning_time=timedelta(minutes=7))

        response = self.get_url("leagues:offenders", pk=lg.pk)
        self.assertContains(response, lg.name)
        self.assertContains(response, lg.abbreviation)
        self.assertContains(response, team.short_name)
        self.assertContains(response, offender.name)

    def test_empty(self):
        association = Association.objects.create(name="Test Association 1", abbreviation="A1", bhv_id=1, source_url="")
        district = District.objects.create(name="Test District 10", bhv_id=10)
        district.associations.add(association)
        season = Season.objects.create(start_year=2025)
        lg = League.objects.create(name="Test L 25", abbreviation="L25", bhv_id=25, district=district, season=season)
        team = Team.objects.create(name="Test Team 251", short_name="T251", bhv_id=251, league=lg)
        punishless = Player.objects.create(name="Test Player 2511", team=team)
        game = Game.objects.create(number=2501, league=lg, home_team=team, guest_team=team)
        Score.objects.create(player=punishless, player_number=6, game=game)
        response = self.get_url("leagues:offenders", pk=lg.pk)
        self.assertNotContains(response, punishless.name)

    def test_not_found(self):
        response = self.get_url("leagues:offenders", pk=1)
        self.assertEqual(response.status_code, 404)
