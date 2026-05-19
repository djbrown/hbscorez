from django.urls import include, path

from clubs.views import detail

app_name = "clubs"

urlpatterns = [
    path("<int:pk>/", include([path("", detail, name="detail")])),
]
