from django.urls import include, path

from leagues.views import detail, games, offenders, scorers, teams

app_name = "leagues"

urlpatterns = [
    path(
        "<int:pk>/",
        include(
            [
                path("", detail, name="detail"),
                path("mannschaften/", teams, name="teams"),
                path("spiele/", games, name="games"),
                path("schuetzen/", scorers, name="scorers"),
                path("straffaellige/", offenders, name="offenders"),
                # path("kalender/", calendar, name="calendar"), # TODO
            ]
        ),
    ),
]
