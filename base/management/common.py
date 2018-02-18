from pathlib import Path

from django.conf import settings

from base.models import Game

REPORTS_PATH = Path(settings.BASE_DIR, 'reports')


def report_path(game):
    return REPORTS_PATH.joinpath(str(game.bhv_id) + '.pdf')


def find_games(bhv_ids: list):
    if bhv_ids:
        return Game.objects.filter(bhv_id__in=bhv_ids)
    else:
        return Game.objects.all()
