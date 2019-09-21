import logging

from django.db import migrations

from base import logic, parsing

from ..models import League

LOGGER = logging.getLogger('hbscorez')


def update_league_names(*_):
    for league in League.objects.all():
        dom = logic.get_html(league.source_url())
        name = parsing.parse_league_name(dom)
        if name != league.name:
            league.name = name
            league.save()
            LOGGER.info('RENAMED LEAGUE: %s', league)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('leagues', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_league_names),
    ]
