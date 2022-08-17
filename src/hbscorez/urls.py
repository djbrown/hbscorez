from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from api import urls as api_urls
from associations import urls as association_urls
from associations.models import Association
from base import urls as base_urls
from districts import urls as district_urls
from districts.models import District
from games import urls as game_urls
from games.models import Game
from leagues import urls as league_urls
from leagues.models import League
from players import urls as player_urls
from players.models import Player
from sports_halls import urls as sports_hall_urls
from teams import urls as team_urls
from teams.models import Team
from users import urls as user_urls
from users.forms import CaptchaRegistrationForm
from users.views import CaptchaRegistrationView

ASSOCIATIONS = {'queryset': Association.objects.get_queryset().order_by('pk')}
DISTRICTS = {'queryset': District.objects.get_queryset().order_by('pk')}
LEAGUES = {'queryset': League.objects.get_queryset().order_by('pk')}
TEAMS = {'queryset': Team.objects.get_queryset().order_by('pk')}
GAMES = {'queryset': Game.objects.get_queryset().order_by('pk')}
PLAYERS = {'queryset': Player.objects.get_queryset().order_by('pk')}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('registrierung/register/',
         CaptchaRegistrationView.as_view(form_class=CaptchaRegistrationForm),
         name='django_registration_register'),
    path('registrierung/', include('django_registration.backends.activation.urls')),
    path('benutzer/', include(user_urls)),
    path('sitemap.xml', sitemap, {'sitemaps': {
        # https://github.com/typeddjango/django-stubs/pull/1111
        'associations': GenericSitemap(ASSOCIATIONS),  # type: ignore[arg-type]
        'districts': GenericSitemap(DISTRICTS),  # type: ignore[arg-type]
        'leagues': GenericSitemap(LEAGUES),  # type: ignore[arg-type]
        'teams': GenericSitemap(TEAMS),  # type: ignore[arg-type]
        'players': GenericSitemap(PLAYERS),  # type: ignore[arg-type]
    }}, name='django.contrib.sitemaps.views.sitemap'),
    path('', include(base_urls)),
    path('verbaende/', include(association_urls)),
    path('kreise/', include(district_urls)),
    path('ligen/', include(league_urls)),
    path('mannschaften/', include(team_urls)),
    path('spiele/', include(game_urls)),
    path('sporthallen/', include(sports_hall_urls)),
    path('spieler/', include(player_urls)),
    path('api/', include(api_urls)),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
