from django.urls import include, path

from districts.views import detail

app_name = "districts"

urlpatterns = [
    path("<int:bhv_id>/", include([path("", detail, name="detail")])),
]
