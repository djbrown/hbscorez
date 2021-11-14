from django.contrib import admin

from .models import League, Season


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    search_fields = ('name', 'abbreviation', 'bhv_id',
                     'district__name', 'district__bhv_id',
                     'season__start_year')


admin.site.register(Season)
