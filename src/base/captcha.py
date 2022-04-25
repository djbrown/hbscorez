import base64

from captcha.image import ImageCaptcha
from django.conf import settings
from django.utils.crypto import get_random_string


def generate_captcha():
    return settings.CAPTCHA \
        if hasattr(settings, 'CAPTCHA') \
        else get_random_string(length=4)


def encode_captcha_image_base64(captcha: str) -> str:
    data = ImageCaptcha().generate(captcha)
    image_bytes = data.read()
    b64_bytes = base64.b64encode(image_bytes)
    return b64_bytes.decode('UTF-8')
