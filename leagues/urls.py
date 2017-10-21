from django.conf.urls import url

from scorers import views as s
from . import views

urlpatterns = [
    url(r'^$', views.league, name='index'),
    url(r'^torjaeger/$', s.league_scorers, name='scorers'),
]
