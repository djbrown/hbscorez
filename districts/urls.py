from django.urls import path, include

from .views import *

app_name = 'districts'

urlpatterns = [
    path('<int:bhv_id>/', include([
        path('', detail, name='detail'),
    ])),
]
