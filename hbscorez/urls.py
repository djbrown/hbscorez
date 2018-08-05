from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import include
from django.urls import path

import associations.urls
import base.urls
import districts.urls
import games.urls
import leagues.urls
import players.urls
import sports_halls.urls
import teams.urls
from associations.models import Association
from districts.models import District
from games.models import Game
from leagues.models import League
from players.models import Player
from teams.models import Team

associations_dict = {'queryset': Association.objects.get_queryset().order_by('pk')}
districts_dict = {'queryset': District.objects.get_queryset().order_by('pk')}
leagues_dict = {'queryset': League.objects.get_queryset().order_by('pk')}
teams_dict = {'queryset': Team.objects.get_queryset().order_by('pk')}
games_dict = {'queryset': Game.objects.get_queryset().order_by('pk')}
players_dict = {'queryset': Player.objects.get_queryset().order_by('pk')}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap..xml', sitemap, {'sitemaps': {
        'associations': GenericSitemap(associations_dict),
        'districts': GenericSitemap(districts_dict),
        'leagues': GenericSitemap(leagues_dict),
        'teams': GenericSitemap(teams_dict),
        'players': GenericSitemap(players_dict),
    }}, name='django.contrib.sitemaps.views.sitemap'),
    path('', include(base.urls)),
    path('verbaende/', include(associations.urls)),
    path('kreise/', include(districts.urls)),
    path('ligen/', include(leagues.urls)),
    path('mannschaften/', include(teams.urls)),
    path('spiele/', include(games.urls)),
    path('sporthallen/', include(sports_halls.urls)),
    path('spieler/', include(players.urls)),

]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
