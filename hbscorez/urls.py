from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

import base.urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(base.urls)),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
