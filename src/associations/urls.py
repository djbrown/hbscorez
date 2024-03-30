from django.urls import include, path

from associations.views import detail, show_all

app_name = "associations"

urlpatterns = [
    path("", show_all, name="list"),
    path("<int:bhv_id>/", include([path("", detail, name="detail")])),
]
