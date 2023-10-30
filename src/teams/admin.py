from django.contrib import admin

from leagues.admin import LEAGUE_SEARCH_FIELDS
from teams.models import Team

TEAM_SEARCH_FIELDS = ['name', 'short_name', 'bhv_id'] + \
    ['league__' + field for field in LEAGUE_SEARCH_FIELDS]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    search_fields = TEAM_SEARCH_FIELDS
