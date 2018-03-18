from django.conf.urls import url

from base.views import *

urlpatterns = [
    url(r'^$', view_home, name='home'),
    url(r'^impressum/$', view_notice, name='notice'),
    url(r'^kontakt/$', view_contact, name='contact'),
    url(r'^verbaende/$', view_associations, name='associations'),
    # todo: (?P<bhv_id>\d+)-(?P<slug>[-\w\d]+)
    url(r'^verband/(?P<bhv_id>\d+)/$', view_association, name='association'),
    url(r'^kreis/(?P<bhv_id>\d+)/$', view_district, name='district'),
    url(r'^liga/(?P<bhv_id>\d+)/$', view_league_overview, name='league_overview'),
    url(r'^liga/(?P<bhv_id>\d+)/mannschaften/$', view_league_teams, name='league_teams'),
    url(r'^liga/(?P<bhv_id>\d+)/spiele/$', view_league_games, name='league_games'),
    url(r'^liga/(?P<bhv_id>\d+)/spieler/$', view_league_players, name='league_players'),
    url(r'^liga/(?P<bhv_id>\d+)/kalender/$', view_league_calendar, name='league_calendar'),
    url(r'^mannschaft/(?P<bhv_id>\d+)/$', view_team_overview, name='team_overview'),
    url(r'^mannschaft/(?P<bhv_id>\d+)/spiele/$', view_team_games, name='team_games'),
    url(r'^mannschaft/(?P<bhv_id>\d+)/spieler/$', view_team_players, name='team_players'),
    url(r'^mannschaft/(?P<bhv_id>\d+)/kalender/$', view_team_calendar, name='team_calendar'),
    url(r'^spieler/(?P<pk>\d+)/$', view_player, name='scorer'),
]
