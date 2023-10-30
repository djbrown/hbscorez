from django.urls import include, path

from players.views import detail

app_name = 'players'

urlpatterns = [
    path('<int:key>/', include([
        path('', detail, name='detail'),
    ])),
]
