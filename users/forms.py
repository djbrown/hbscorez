from django import forms
from django.core.exceptions import ValidationError

from players.models import Player
from teams.models import Team


class LinkForm(forms.Form):
    team_bhv_id = forms.IntegerField()
    player_name = forms.CharField(max_length=100)

    def clean_team_bhv_id(self):
        team_bhv_id = self.cleaned_data.get('team_bhv_id')
        try:
            team = Team.objects.get(bhv_id=team_bhv_id)
        except Team.DoesNotExist:
            raise ValidationError('Mannschaft konnte nicht gefunden werden.')
        # todo: check if user has no player on current year
        self.cleaned_data['team'] = team
        return team_bhv_id

    def clean_player_name(self):
        team_bhv_id = self.cleaned_data.get('team_bhv_id')
        player_name = self.cleaned_data.get('player_name')
        try:
            player = Player.objects.get(team__bhv_id=team_bhv_id, name__iexact=player_name)
        except Player.DoesNotExist:
            raise ValidationError('Spieler konnte nicht gefunden werden.')

        if player.user != = None:
            raise ValidationError('Spieler wurde bereits verknüpft.')

        self.cleaned_data['player'] = player

        return player_name
