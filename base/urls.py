from django.urls import path

from base.views import *

urlpatterns = [
    path('', view_home, name='home'),
    path('impressum/', view_notice, name='notice'),
    path('datenschutz/', view_privacy, name='privacy'),
    # path('kontakt/', view_contact, name='contact'),
]
