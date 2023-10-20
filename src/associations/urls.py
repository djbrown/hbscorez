from django.urls import path, include

from associations.views import show_all, detail

app_name = 'associations'

urlpatterns = [
    path('', show_all, name='list'),
    path('<int:bhv_id>/', include([
        path('', detail, name='detail'),
    ])),
]
