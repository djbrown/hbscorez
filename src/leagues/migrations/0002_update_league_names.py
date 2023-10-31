import logging

from django.db import migrations

from base import http, parsing

LOGGER = logging.getLogger('hbscorez')


def update_league_names(apps, _):
    league_model = apps.get_model("leagues", "League")
    for league in league_model.objects.all():
        html = http.get_text(league.source_url())
        dom = parsing.html_dom(html)
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
