import logging

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from players.models import Player
from teams.models import Team

LOGGER = logging.getLogger('hbscorez')


class LinkForm(forms.Form):
    team_bhv_id = forms.IntegerField()
    player_name = forms.CharField(max_length=100)

    user: User = None

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super(LinkForm, self).__init__(*args, **kwargs)

    def clean_team_bhv_id(self):
        team_bhv_id = self.cleaned_data.get('team_bhv_id')

        try:
            team = Team.objects.get(bhv_id=team_bhv_id)
        except Team.DoesNotExist:
            raise ValidationError('Mannschaft konnte nicht gefunden werden.')

        self.cleaned_data['team'] = team
        return team_bhv_id

    def clean(self):
        team = self.cleaned_data.get('team')
        player_name = self.cleaned_data.get('player_name')

        if not team or not player_name:
            return None

        try:
            player = Player.objects.get(team=team, name__iexact=player_name)
        except Player.DoesNotExist:
            self.add_error('player_name', 'Spieler konnte nicht gefunden werden.')
            return None

        if player.user is not None:
            self.add_error('player_name', 'Spieler ist bereits verknüpft.')
            return None

        self.cleaned_data['player'] = player
        return self.cleaned_data
