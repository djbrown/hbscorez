from django.urls import path

from api import views

app_name = "api"

urlpatterns = [
    path("associations/", views.associations, name="associations"),
    path("associations/<int:pk>/districts/", views.association_districts, name="association_districts"),
    path("seasons/", views.seasons, name="seasons"),
    path(
        "districts/<int:pk>/seasons/<int:start_year>/leagues/",
        views.district_season_leagues,
        name="district_season_leagues",
    ),
    path("leagues/<int:pk>/teams/", views.league_teams, name="league_teams"),
]
