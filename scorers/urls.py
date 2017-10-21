from django.conf.urls import url

import associations.views
from . import views

urlpatterns = [
    url(r'^(?P<assoc_abbr>.+)/(?P<dist_abbr>.+)/(?P<league_abbr>.+)/torjaeger/$', views.league_scorers, name='scorers'),
    url(r'^(?P<assoc_abbr>.+)/(?P<dist_abbr>.+)/(?P<league_abbr>.+)/$', views.league_overview, name='league'),
    url(r'^(?P<assoc_abbr>.+)/(?P<dist_abbr>.+)/$', views.district_overview, name='district'),
]
