from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from base.views import ContactView

app_name = "base"

urlpatterns = [  # pylint: disable=invalid-name
    path("", TemplateView.as_view(template_name="base/home.j2"), name="home"),
    path("impressum/", TemplateView.as_view(template_name="base/imprint.j2"), name="imprint"),
    path("datenschutz/", TemplateView.as_view(template_name="base/privacy.j2"), name="privacy"),
    path("kontakt/", ContactView.as_view(), name="contact_form"),
    path(
        route="kontakt/gesendet/",
        name="contact_form_sent",
        view=TemplateView.as_view(template_name="django_contact_form/contact_form_sent.html"),
    ),
    path("wartung.html", RedirectView.as_view(pattern_name="base:home"), name="maintenance"),
]
