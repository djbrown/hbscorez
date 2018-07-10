from django.urls import path, include

from .views import *

app_name = 'players'

urlpatterns = [
    path('<int:pk>/', include([
        path('', detail, name='detail'),
    ])),
]
