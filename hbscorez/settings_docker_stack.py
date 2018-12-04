from typing import Optional

from .settings import *  # noqa # pylint: disable=all

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

MATOMO_URL: Optional[str] = 'https://matomo.hbscorez.localhost/'  # CHANGEME
