import requests
from django.core.management import BaseCommand

from base.management.report import REPORTS_PATH, report_path
from base.models import Game


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--force-update', '-f', action='store_true',
                            help='force download and overwrite if report already exists')

    def handle(self, *args, **options):
        REPORTS_PATH.mkdir(parents=True, exist_ok=True)

        for game in Game.objects.all():
            if not report_path(game).is_file():
                self.stdout.write('DOWNLOADING Report {}'.format(game.bhv_id))
                download_report(game)
            elif options['force_update']:
                self.stdout.write('REDOWNLOADING Report {}'.format(game.bhv_id))
                download_report(game)
            else:
                self.stdout.write('EXISTING Report {}'.format(game.bhv_id))


def download_report(game):
    response = requests.get(game.report_url(), stream=True)
    report_path(game).write_bytes(response.content)
