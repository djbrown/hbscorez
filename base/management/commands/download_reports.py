import requests
from django.core.management import BaseCommand

from base.management.common import REPORTS_PATH, report_path, find_games


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--games', '-g', nargs='+', type=int, metavar='sGID',
                            help="sGIDs of games whose reports are to be downloaded.")
        parser.add_argument('--force-update', '-f', action='store_true',
                            help='force download and overwrite if report already exists')

    def handle(self, *args, **options):
        REPORTS_PATH.mkdir(parents=True, exist_ok=True)
        
        bugged_reports = [567811]
        
        for game in find_games(options['games']):
            if game.bhv_id in bugged_reports:
                self.stdout.write('SKIPPING Report {} (hardcoded ignore list)'.format(game.bhv_id))
            elif not report_path(game).is_file():
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
