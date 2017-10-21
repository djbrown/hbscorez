from django.conf.urls import url, include

from scorers import views as s
from . import views

urlpatterns = [
    url(r'^$', views.association, name='index'),
    url(r'^(?P<dist_abbr>[a-z]+)/', include('districts.urls', namespace='dist')),
]
