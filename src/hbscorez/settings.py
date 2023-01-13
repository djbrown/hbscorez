from pathlib import Path
from typing import Optional

ROOT_DIR: Path = Path.cwd()

SECRET_KEY = ' '  # noqa

DEBUG = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django_registration',
    'django_contact_form',
    'axes',
    'base',
    'associations',
    'districts',
    'leagues',
    'teams',
    'sports_halls',
    'games',
    'players',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
    'base.middleware.env.EnvironmentMiddleware',
]

ROOT_URLCONF = 'hbscorez.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'base.context_processors.matomo',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'hbscorez.jinja2_env.environment',
            'context_processors': [
                'base.context_processors.matomo',
            ],
        },
    },
]

WSGI_APPLICATION = 'hbscorez.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ROOT_DIR / 'db.sqlite3',
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'de'

TIME_ZONE = 'Europe/Berlin'

USE_L10N = True


# logging

LOGGING: dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname:8} {asctime} {module} - {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname:8} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': ROOT_DIR / 'hbscorez.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail': {
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
            # 'reporter_class': 'base.error_reporter.CustomErrorReporter', # new in django 3
        },
    },
    'loggers': {
        'hbscorez': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'mail': {
            'handlers': ['mail'],
        },
    },
}


# static files

STATIC_ROOT = ROOT_DIR / 'static'

STATIC_URL = '/static/'

MEDIA_ROOT = ROOT_DIR / 'media'

MEDIA_URL = '/media/'


# email

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'

EMAIL_FILE_PATH = ROOT_DIR / 'mails'

MANAGERS = [('manager', 'manager@localhost')]

ADMINS = [('admin', 'admin@localhost')]


# test

TEST_RUNNER = 'base.tests.base.Runner'


# auth

LOGIN_REDIRECT_URL = 'users:profile'

LOGIN_URL = 'users:login'


# django-axes

AXES_COOLOFF_TIME = 24

AXES_LOCKOUT_TEMPLATE = 'users/login.html'


# django-registration

ACCOUNT_ACTIVATION_DAYS = 3


# custom settings

PUBLIC_NAMES = True

MATOMO_URL: Optional[str] = None

REPORTS_PATH = ROOT_DIR / 'reports'

ROOT_SOURCE_URL = 'https://spo.handball4all.de/'

NEW_ROOT_SOURCE_URL = 'https://www.handball4all.de/'

BROWSER_TIMEOUT = 3
