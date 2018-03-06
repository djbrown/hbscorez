from pathlib import Path

from django.conf import settings

from base.models import Game

REPORTS_PATH = Path(settings.BASE_DIR, 'reports')


def report_path(game):
    return REPORTS_PATH.joinpath(str(game.report_number) + '.pdf')


def find_games(report_number: list):
    if report_number:
        return Game.objects.filter(report_number=report_number)
    else:
        return Game.objects.all()
