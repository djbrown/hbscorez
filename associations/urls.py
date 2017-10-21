from django.conf.urls import url

from scorers import views as s
from . import views

urlpatterns = [
    url(r'^$', views.association_overview, name='index'),
    url(r'^(?P<dist_abbr>.+)/(?P<league_abbr>.+)/torjaeger/$', s.league_scorers, name='scorers'),
    url(r'^(?P<dist_abbr>.+)/(?P<league_abbr>.+)/$', s.league_overview, name='league'),
    url(r'^(?P<dist_abbr>[a-z]+)/$', s.district_overview, name='district'),
]
