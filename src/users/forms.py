import logging

from django import forms
from django.core.exceptions import ValidationError
from django_registration.forms import RegistrationForm

from base.captcha import encode_captcha_image_base64, generate_captcha
from players.models import Player
from teams.models import Team

LOGGER = logging.getLogger('hbscorez')


class CaptchaRegistrationForm(RegistrationForm):
    captcha = forms.CharField(label='Captcha')
    captcha_image_base64 = None
    request = None

    def init_captcha(self, request):
        self.request = request
        session_captcha = request.session.get('captcha')

        if session_captcha is None:
            session_captcha = generate_captcha()
            request.session['captcha'] = session_captcha

        self.captcha = session_captcha
        self.captcha_image_base64 = encode_captcha_image_base64(self.captcha)

    def clean_captcha(self):
        input_captcha = self.cleaned_data.get('captcha')
        session_captcha = self.request.session.get('captcha')

        self.captcha = generate_captcha()
        self.request.session['captcha'] = self.captcha
        self.captcha_image_base64 = encode_captcha_image_base64(self.captcha)

        if input_captcha != session_captcha:
            raise ValidationError('Falsches Captcha.')

        return input_captcha


class LinkForm(forms.Form):
    team_bhv_id = forms.IntegerField()
    player_name = forms.CharField(max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_team_bhv_id(self):
        team_bhv_id = self.cleaned_data.get('team_bhv_id')

        try:
            team = Team.objects.get(bhv_id=team_bhv_id)
        except Team.DoesNotExist as exc:
            raise ValidationError('Mannschaft konnte nicht gefunden werden.') from exc

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
