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
    url(r'^liga/(?P<bhv_id>\d+)/$', view_league, name='league'),
    url(r'^liga/(?P<bhv_id>\d+)/torjaeger/$', view_league_players, name='league_players'),
    url(r'^team/(?P<bhv_id>\d+)/$', view_team, name='team'),
    url(r'^spieler/(?P<pk>\d+)/$', view_player, name='player'),
]
