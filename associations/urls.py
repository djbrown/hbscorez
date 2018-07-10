from django.urls import path, include

from .views import list, detail

app_name = 'associations'

urlpatterns = [
    path('', list, name='list'),
    path('<int:bhv_id>/', include([
        path('', detail, name='detail'),
    ])),
]
