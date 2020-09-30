
import base64

from captcha.image import ImageCaptcha
from contact_form.forms import ContactForm
from contact_form.views import ContactFormView
from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string


def view_home(request):
    return render(request, 'base/home.j2')


def view_notice(request):
    return render(request, 'base/imprint.j2')


def view_privacy(request):
    return render(request, 'base/privacy.j2')


image = ImageCaptcha(fonts=['/mnt/c/Windows/Fonts/cour.ttf'])


def generate_captcha():
    return get_random_string(length=4)


def encode_captcha_image_base64(captcha: str) -> str:
    data = image.generate(captcha)
    image_bytes = data.read()
    b64_bytes = base64.b64encode(image_bytes)
    return b64_bytes.decode('UTF-8')


class Form(ContactForm):
    captcha = forms.CharField(label="Captcha")

    def __init__(self, *args, **kwargs):
        session_captcha = kwargs.get("request").session.get('captcha')

        if session_captcha is None:
            session_captcha = generate_captcha()
            kwargs.get("request").session['captcha'] = session_captcha

        self.captcha = session_captcha
        self.captcha_image_base64 = encode_captcha_image_base64(self.captcha)

        super().__init__(*args, **kwargs)

    def clean_captcha(self):
        input_captcha = self.cleaned_data.get('captcha')
        session_captcha = self.request.session.get('captcha')

        self.captcha = generate_captcha()
        self.request.session['captcha'] = self.captcha
        self.captcha_image_base64 = encode_captcha_image_base64(self.captcha)

        if input_captcha != session_captcha:
            raise ValidationError('Falsches Captcha.')

        return input_captcha


class ContactView(ContactFormView):
    form_class = Form
    success_url = reverse_lazy("base:contact_form_sent")
