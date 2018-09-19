from django.urls import include, path

from .views import detail

app_name = 'players'

urlpatterns = [
    path('<int:pk>/', include([
        path('', detail, name='detail'),
    ])),
]
