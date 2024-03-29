from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.defaultfilters import date, time
from django.urls import reverse
from jinja2 import Environment

from base.templatetags.scores_extras import game_outcome_badge, team_logo_url, team_outcome_badge


def environment(**options):
    options['autoescape'] = True
    env = Environment(trim_blocks=True, lstrip_blocks=True, **options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
        'team_logo_url': team_logo_url,
        'date': date,
        'time': time,
        'team_outcome_badge': team_outcome_badge,
        'game_outcome_badge': game_outcome_badge,
    })
    return env
