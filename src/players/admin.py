from django.contrib import admin

from games.admin import GAME_SEARCH_FIELDS
from teams.admin import TEAM_SEARCH_FIELDS

from .models import Player, ReportsBlacklist, Score

PLAYER_SEARCH_FIELDS = ['name'] + \
    ['team__' + field for field in TEAM_SEARCH_FIELDS]

SCORE_SEARCH_FIELDS = ['player_number'] + \
    ['player__' + field for field in PLAYER_SEARCH_FIELDS] + \
    ['game__' + field for field in GAME_SEARCH_FIELDS]


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    search_fields = PLAYER_SEARCH_FIELDS


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    search_fields = SCORE_SEARCH_FIELDS


@admin.register(ReportsBlacklist)
class ReportsBlacklistAdmin(admin.ModelAdmin):
    search_fields = ["report_number"]
