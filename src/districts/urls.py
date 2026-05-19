from django.urls import include, path

from districts.views import detail

app_name = "districts"

urlpatterns = [
    path("<int:pk>/", include([path("", detail, name="detail")])),
]
