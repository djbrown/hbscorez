from django.urls import path, include

from .views import *

app_name = 'teams'
urlpatterns = [
    path('<int:bhv_id>/', include([
        path('', detail, name='detail'),
        # path('spieler/', players, name=players'),
        path('spiele/', games, name='games'),
        path('schützen/', scorers, name='scorers'),
        path('strafen/', penalties, name='penalties'),
        path('kalender/', calendar, name='calendar'),
    ])),
]
