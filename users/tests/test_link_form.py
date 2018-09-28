from django.contrib.auth.models import User
from django.test import TestCase

from districts.models import District
from leagues.models import League, Season
from players.models import Player
from teams.models import Team

from ..forms import LinkForm


class TestLinkForm(TestCase):
    def test_simple(self):
        district = District.objects.create(bhv_id=1)
        season = Season.objects.create(start_year=2)
        league = League.objects.create(bhv_id=3, district=district, season=season)
        team = Team.objects.create(bhv_id=4, league=league)
        player = Player.objects.create(name='player name', team=team)

        form_data = {'team_bhv_id': team.bhv_id, 'player_name': player.name}
        form = LinkForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_player_name_ignore_case(self):
        district = District.objects.create(bhv_id=1)
        season = Season.objects.create(start_year=2)
        league = League.objects.create(bhv_id=3, district=district, season=season)
        team = Team.objects.create(bhv_id=4, league=league)
        Player.objects.create(name='Player Name', team=team)

        form_data = {'team_bhv_id': team.bhv_id, 'player_name': 'player name'}
        form = LinkForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_team_does_not_exist(self):
        district = District.objects.create(bhv_id=1)
        season = Season.objects.create(start_year=2)
        league = League.objects.create(bhv_id=3, district=district, season=season)
        team = Team.objects.create(bhv_id=4, league=league)
        player = Player.objects.create(name='player name', team=team)

        form_data = {'team_bhv_id': 100, 'player_name': player.name}
        form = LinkForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'team_bhv_id': ['Mannschaft konnte nicht gefunden werden.']})

    def test_player_does_not_exist(self):
        district = District.objects.create(bhv_id=1)
        season = Season.objects.create(start_year=2)
        league = League.objects.create(bhv_id=3, district=district, season=season)
        team = Team.objects.create(bhv_id=4, league=league)

        form_data = {'team_bhv_id': team.bhv_id, 'player_name': 'error'}
        form = LinkForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'player_name': ['Spieler konnte nicht gefunden werden.']})

    def test_team_and_player_do_not_exist(self):
        form_data = {'team_bhv_id': 100, 'player_name': 'error'}
        form = LinkForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'team_bhv_id': ['Mannschaft konnte nicht gefunden werden.']})

    def test_player_already_linked(self):
        district = District.objects.create(bhv_id=1)
        season = Season.objects.create(start_year=2)
        league = League.objects.create(bhv_id=3, district=district, season=season)
        team = Team.objects.create(bhv_id=4, league=league)
        user = User.objects.create(username='username')
        player = Player.objects.create(name='player name', team=team, user=user)

        form_data = {'team_bhv_id': team.bhv_id, 'player_name': player.name}
        form = LinkForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'player_name': ['Spieler ist bereits verknüpft.']})
