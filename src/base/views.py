
from contact_form.views import ContactFormView
from django.urls import reverse_lazy
from .forms import CaptchaContactForm


class ContactView(ContactFormView):
    form_class = CaptchaContactForm
    success_url = reverse_lazy("base:contact_form_sent")
