from django.contrib import admin

from leagues.admin import LEAGUE_SEARCH_FIELDS
from teams.admin import TEAM_SEARCH_FIELDS

from .models import Game

GAME_SEARCH_FIELDS = ['number'] + \
    ['home_team__' + field for field in TEAM_SEARCH_FIELDS] + \
    ['guest_team__' + field for field in TEAM_SEARCH_FIELDS] + \
    ['league__' + field for field in LEAGUE_SEARCH_FIELDS]


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    search_fields = GAME_SEARCH_FIELDS
