from django.conf.urls import url

from scorers import views as s
from . import views

urlpatterns = [
    url(r'^$', views.district, name='index'),
    url(r'^(?P<league_abbr>.+)/torjaeger/$', s.league_scorers, name='scorers'),
    url(r'^(?P<league_abbr>.+)/$', s.league_overview, name='league'),
]
