from django.conf import settings
from django.conf.urls.static import static

from base.views import home
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^', include('scorers.urls', namespace='scorers')),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
