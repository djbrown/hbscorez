from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.association, name='index'),
    url(r'^(?P<dist_abbr>[^/]+)/', include('districts.urls', namespace='dist')),
]
