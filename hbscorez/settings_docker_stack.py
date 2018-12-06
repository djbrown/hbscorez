from typing import Optional

from .settings import *  # noqa # pylint: disable=all

SECRET_KEY = '12345678901234567890123456789012345678901234567890'  # CHANGEME

DEBUG = False

ALLOWED_HOSTS = ['hbscorez.localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hbscorezdb',  # CHANGEME
        'USER': 'hbscorezdbuser',  # CHANGEME
        'PASSWORD': 'hbscorezdbpassword',  # CHANGEME
        'HOST': 'hbscorezdb',  # CHANGEME
        'PORT': '5432',
    }
}

CSRF_COOKIE_SECURE = True

X_FRAME_OPTIONS = 'DENY'

SECURE_HSTS_SECONDS = 10

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_BROWSER_XSS_FILTER = True

# SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True

SECURE_HSTS_PRELOAD = True

MATOMO_URL: Optional[str] = 'https://matomo.hbscorez.localhost/'  # CHANGEME
