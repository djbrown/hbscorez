from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from leagues.admin import LEAGUE_SEARCH_FIELDS
from teams.admin import TEAM_SEARCH_FIELDS

from games.models import Game, GameOutcome

GAME_SEARCH_FIELDS = ['number'] + \
    ['home_team__' + field for field in TEAM_SEARCH_FIELDS] + \
    ['guest_team__' + field for field in TEAM_SEARCH_FIELDS] + \
    ['league__' + field for field in LEAGUE_SEARCH_FIELDS]


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('number', 'league_year', 'show_opening_whistle', 'league_name',
                    'home_team_name', 'guest_team_name', 'report', 'home_goals', 'guest_goals', 'spectators')
    list_filter = ('league__season',)
    search_fields = GAME_SEARCH_FIELDS

    @admin.display(description='Heimmannschaft')
    def home_team_name(self, obj: Game) -> str:
        url = reverse('admin:teams_team_change', args=(obj.home_team.pk,))
        name = obj.home_team.name
        if obj.outcome() == GameOutcome.HOME_WIN:
            return format_html('<a style="color:#28a745;" href="{}">{}</a>', url, name)
        if obj.outcome() == GameOutcome.TIE:
            return format_html('<a style="color:#ffc107;" href="{}">{}</a>', url, name)
        return format_html('<a style="color:#dc3545;" href="{}">{}</a>', url, name)

    @admin.display(description='Gastmannschaft')
    def guest_team_name(self, obj: Game) -> str:
        url = reverse('admin:teams_team_change', args=(obj.guest_team.pk,))
        name = obj.guest_team.name
        if obj.outcome() == GameOutcome.AWAY_WIN:
            return format_html('<a style="color:#28a745;" href="{}">{}</a>', url, name)
        if obj.outcome() == GameOutcome.TIE:
            return format_html('<a style="color:#ffc107;" href="{}">{}</a>', url, name)
        return format_html('<a style="color:#dc3545;" href="{}">{}</a>', url, name)

    @admin.display(description='Saison', ordering='league__season__start_year')
    def league_year(self, obj: Game) -> str:
        return str(obj.league.season)

    @admin.display(description='Liga')
    def league_name(self, obj: Game) -> str:
        return str(obj.league.name)

    @admin.display(description='Anpfiff', ordering='opening_whistle')
    def show_opening_whistle(self, obj: Game) -> str | None:
        if not obj.opening_whistle:
            return None
        return obj.opening_whistle.strftime('%d.%m.%Y %H:%M')

    @admin.display(description='Bericht')
    def report(self, obj: Game) -> str | None:
        report_nr = obj.report_number
        if report_nr is None:
            return None
        url = obj.report_source_url()
        return format_html('<a href="{}">{}</a>', url, report_nr)
