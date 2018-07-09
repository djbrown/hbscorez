from django.urls import path

from base.views import *

urlpatterns = [
    path('', view_home, name='home'),
    path('impressum/', view_notice, name='notice'),
    path('datenschutz/', view_privacy, name='privacy'),
    # path('kontakt/', view_contact, name='contact'),
    path('verbaende/', view_associations, name='associations'),
    # todo: <int:bhv_id>-<slug:slug>
    path('verband/<int:bhv_id>/', view_association, name='association'),
    path('kreis/<int:bhv_id>/', view_district, name='district'),
    path('liga/<int:bhv_id>/', view_league_overview, name='league_overview'),
    path('liga/<int:bhv_id>/mannschaften/', view_league_teams, name='league_teams'),
    path('liga/<int:bhv_id>/spiele/', view_league_games, name='league_games'),
    path('liga/<int:bhv_id>/schützen/', view_league_scorers, name='league_scorers'),
    path('liga/<int:bhv_id>/strafen/', view_league_penalties, name='league_penalties'),
    path('liga/<int:bhv_id>/kalender/', view_league_calendar, name='league_calendar'),
    path('mannschaft/<int:bhv_id>/', view_team_overview, name='team_overview'),
    # path('mannschaft/<int:bhv_id>/spieler/', view_team_players, name='team_players'),
    path('mannschaft/<int:bhv_id>/spiele/', view_team_games, name='team_games'),
    path('mannschaft/<int:bhv_id>/schützen/', view_team_scorers, name='team_scorers'),
    path('mannschaft/<int:bhv_id>/strafen/', view_team_penalties, name='team_penalties'),
    path('mannschaft/<int:bhv_id>/kalender/', view_team_calendar, name='team_calendar'),
    path('spieler/<int:pk>/', view_player, name='player'),
]
