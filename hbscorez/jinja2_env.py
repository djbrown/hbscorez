from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse

from jinja2 import Environment

from scorers.templatetags.scores_extras import club_logo_url, place


def environment(**options):
    options['trim_blocks'] = True
    options['lstrip_blocks'] = True
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
        'club_logo_url': club_logo_url,
        'place': place,
    })
    return env
