from base.views import home
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^torjaeger/', include('scorers.urls', namespace='scorers')),
    url(r'^admin/', admin.site.urls),
]
