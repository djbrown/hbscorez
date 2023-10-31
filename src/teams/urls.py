from django.urls import include, path

from teams.views import calendar, detail, games, offenders, players, scorers

app_name = 'teams'
urlpatterns = [
    path('<int:bhv_id>/', include([
        path('', detail, name='detail'),
        path('spieler/', players, name='players'),
        path('spiele/', games, name='games'),
        path('schuetzen/', scorers, name='scorers'),
        path('straffaellige/', offenders, name='offenders'),
        path('kalender/', calendar, name='calendar'),
    ])),
]
