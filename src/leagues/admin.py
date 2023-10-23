from django.contrib import admin

from districts.admin import DISTRICT_SEARCH_FIELDS

from .models import League, LeagueName, Season

SEASON_SEARCH_FIELDS = ['start_year']

LEAGUE_SEARCH_FIELDS = ['name', 'abbreviation', 'bhv_id'] + \
    ['district__' + field for field in DISTRICT_SEARCH_FIELDS] +\
    ['season__' + field for field in SEASON_SEARCH_FIELDS]


@ admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    search_fields = SEASON_SEARCH_FIELDS


@ admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('bhv_id', 'name', 'season')
    list_display_links = ('bhv_id', 'name')
    list_filter = ('season',)
    search_fields = LEAGUE_SEARCH_FIELDS


@ admin.register(LeagueName)
class LeagueNameAdmin(admin.ModelAdmin):
    search_fields = ['bhv_id', 'name']
