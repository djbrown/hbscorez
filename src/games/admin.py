from django.contrib import admin

from .models import Game


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    search_fields = ('number', 'home_team__name', 'guest_team__name', 'league__name', 'league__district__name',
                     'league__district__bhv_id', 'league__season__start_year', 'league__bhv_id')
