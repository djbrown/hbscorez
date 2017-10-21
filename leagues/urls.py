from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.league, name='index'),
    url(r'^torjaeger/$', views.league_scorers, name='scorers'),
]
