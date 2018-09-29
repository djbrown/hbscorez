from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from players.models import Player
from teams.models import Team


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

        if self.user.player_set.exists():
            raise ValidationError('Saison ist bereits verknüpft.')

        self.cleaned_data['team'] = team
        return team_bhv_id

    def clean_player_name(self):
        team_bhv_id = self.cleaned_data.get('team_bhv_id')
        player_name = self.cleaned_data.get('player_name')

        try:
            self.clean_team_bhv_id()
        except ValidationError:
            return player_name

        try:
            player = Player.objects.get(team__bhv_id=team_bhv_id, name__iexact=player_name)
        except Player.DoesNotExist:
            raise ValidationError('Spieler konnte nicht gefunden werden.')

        if player.user is not None:
            raise ValidationError('Spieler ist bereits verknüpft.')

        self.cleaned_data['player'] = player

        return player_name
