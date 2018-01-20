from django.conf.urls import url

from base.views import *

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^impressum/$', notice, name='notice'),
    url(r'^kontakt/$', contact, name='contact'),
    url(r'^verbaende/$', associations, name='associations'),
    url(r'^verband/(?P<id>\d+)/$', association, name='association'),
    url(r'^kreis/(?P<id>\d+)/$', district, name='district'),
    url(r'^liga/(?P<id>\d+)/$', league, name='league'),
    url(r'^liga/(?P<id>\d+)/torjaeger/$', league_scorers, name='league_scorers'),
    url(r'^teams/(?P<id>\d+)/$', team, name='team'),
]
