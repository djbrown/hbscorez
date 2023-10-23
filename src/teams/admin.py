from django.contrib import admin

from leagues.admin import LEAGUE_SEARCH_FIELDS
from .models import Team

TEAM_SEARCH_FIELDS = ['name', 'short_name', 'bhv_id'] + \
    ['league__' + field for field in LEAGUE_SEARCH_FIELDS]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'season', 'get_league')
    list_filter = ('league__season',)
    search_fields = TEAM_SEARCH_FIELDS

    @admin.display(description='Saison')
    def season(self, obj: Team) -> str:
        return str(obj.league.season)
    
    @admin.display(description='Liga')
    def get_league(self, obj: Team) -> str:
        return str(obj.league.name)
