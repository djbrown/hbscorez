from contact_form.forms import ContactForm
from django import forms
from django.core.exceptions import ValidationError

from .captcha import encode_captcha_image_base64, generate_captcha


class CaptchaContactForm(ContactForm):
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
