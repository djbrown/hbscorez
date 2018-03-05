from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap

import base.urls
from base.models import *

associations_dict = {'queryset': Association.objects.get_queryset().order_by('pk')}
districts_dict = {'queryset': District.objects.get_queryset().order_by('pk')}
leagues_dict = {'queryset': League.objects.get_queryset().order_by('pk')}
teams_dict = {'queryset': Team.objects.get_queryset().order_by('pk')}
players_dict = {'queryset': Player.objects.get_queryset().order_by('pk')}

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': {
        'associations': GenericSitemap(associations_dict),
        'districts': GenericSitemap(districts_dict),
        'leagues': GenericSitemap(leagues_dict),
        'teams': GenericSitemap(teams_dict),
        'players': GenericSitemap(players_dict),
    }}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^', include(base.urls)),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
