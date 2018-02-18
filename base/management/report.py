from pathlib import Path

from django.conf import settings

REPORTS_PATH = Path(settings.BASE_DIR, 'reports')


def report_path(game):
    return REPORTS_PATH.joinpath(str(game.bhv_id) + '.pdf')
