from pathlib import Path

import requests
from django.conf import settings
from django.core.management import BaseCommand

from base.models import Game

reports_root = Path(settings.REPORTS_ROOT)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--force-update', '-f', action='store_true',
                            help='force download and overwrite if report already exists')

    def handle(self, *args, **options):
        reports_root.mkdir(parents=True, exist_ok=True)

        for game in Game.objects.all():
            if not create_report_path(game).is_file():
                self.stdout.write('DOWNLOADING Report {}'.format(game.bhv_id))
                download_report(game)
            elif options['force_update']:
                self.stdout.write('REDOWNLOADING Report {}'.format(game.bhv_id))
                download_report(game)
            else:
                self.stdout.write('SKIPPING Report {} (already exists)'.format(game.bhv_id))


def create_report_path(game):
    return reports_root.joinpath(str(game.bhv_id) + '.pdf')


def download_report(game):
    response = requests.get(game.report_url(), stream=True)
    create_report_path(game).write_bytes(response.content)
