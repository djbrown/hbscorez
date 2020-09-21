from django.contrib import admin

from .models import League, Season


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    search_fields = ('name', 'abbreviation', 'district__name', 'district__bhv_id', 'season__start_year', 'bhv_id')


admin.site.register(Season)
