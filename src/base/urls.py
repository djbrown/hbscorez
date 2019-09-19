from django.urls import path

from base.views import view_home, view_notice, view_privacy

app_name = 'base'

urlpatterns = [  # pylint: disable=invalid-name
    path('', view_home, name='home'),
    path('impressum/', view_notice, name='notice'),
    path('datenschutz/', view_privacy, name='privacy'),
]
