from django.urls import path
from django.views.generic import TemplateView

from base.views import ContactView, view_home, view_notice, view_privacy

app_name = 'base'

urlpatterns = [  # pylint: disable=invalid-name
    path('', view_home, name='home'),
    path('impressum/', view_notice, name='notice'),
    path('datenschutz/', view_privacy, name='privacy'),
    # path('kontakt/', include('contact_form.akismet_urls')),
    # path('kontakt/', include('contact_form.urls')),
    path("kontakt/", ContactView.as_view(), name="contact_form"),
    path(
        "kontakt/gesendet/",
        TemplateView.as_view(template_name="contact_form/contact_form_sent.html"),
        name="contact_form_sent",
    ),
]
