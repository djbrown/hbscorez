from django.urls import include, path

from clubs.views import detail

app_name = "clubs"

urlpatterns = [
    path("<int:bhv_id>/", include([path("", detail, name="detail")])),
]
