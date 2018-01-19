from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse

from jinja2 import Environment

from base.templatetags.scores_extras import team_logo_url, place


def environment(**options):
    options['trim_blocks'] = True
    options['lstrip_blocks'] = True
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
        'team_logo_url': team_logo_url,
        'place': place,
    })
    return env
