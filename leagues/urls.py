from django.urls import include, path

from .views import calendar, detail, games, offenders, scorers, teams

app_name = 'leagues'

urlpatterns = [
    # todo: <int:bhv_id>-<slug:slug>
    path('<int:bhv_id>/', include([
        path('', detail, name='detail'),
        path('mannschaften/', teams, name='teams'),
        path('spiele/', games, name='games'),
        path('schützen/', scorers, name='scorers'),
        path('straffällige/', offenders, name='offenders'),
        path('kalender/', calendar, name='calendar'),
    ])),
]
