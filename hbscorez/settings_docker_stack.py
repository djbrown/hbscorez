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


# email

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'localhost'  # CHANGEME

# EMAIL_PORT = 25  # CHANGEME

# EMAIL_USE_TLS = False  # CHANGEME

# EMAIL_USE_SSL = False  # CHANGEME

EMAIL_HOST_USER = 'email@localhost'  # CHANGEME

EMAIL_HOST_PASSWORD = 'emailpassword'  # CHANGEME

SERVER_EMAIL = 'server@localhost'  # CHANGEME

DEFAULT_FROM_EMAIL = 'noreply@localhost'  # CHANGEME

MANAGERS = [('Manager', DEFAULT_FROM_EMAIL)]  # CHANGEME

ADMINS = [('Admin', DEFAULT_FROM_EMAIL)]  # CHANGEME


# security

CSRF_COOKIE_SECURE = True

X_FRAME_OPTIONS = 'DENY'

SECURE_HSTS_SECONDS = 10

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_BROWSER_XSS_FILTER = True

# SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True

SECURE_HSTS_PRELOAD = True

# custom settings

PUBLIC_NAMES = False

MATOMO_URL: Optional[str] = 'https://matomo.hbscorez.localhost/'  # CHANGEME
