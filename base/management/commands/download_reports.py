from pathlib import Path

import requests
from django.conf import settings
from django.core.management import BaseCommand

from base import models
from base.middleware import env


class Command(BaseCommand):
    options = {}

    def add_arguments(self, parser):
        parser.add_argument('--force-update', '-f', action='store_true',
                            help='force download and overwrite if report already exists')
        parser.add_argument('--associations', '-a', nargs='+', type=int, metavar='orgGrpID',
                            help="orgGrpIDs of Associations whose games reports shall be downloaded.")
        parser.add_argument('--districts', '-d', nargs='+', type=int, metavar='orgID',
                            help="orgIDs of Districts whose games reports shall be downloaded.")
        parser.add_argument('--leagues', '-l', nargs='+', type=int, metavar='score',
                            help="sGIDs of Leagues whose games reports shall be downloaded.")
        parser.add_argument('--games', '-g', nargs='+', type=int, metavar='game number',
                            help="numbers of Games whose reports shall be downloaded.")
        parser.add_argument('--skip-games', '-G', nargs='+', type=int, metavar='game number',
                            help="numbers of Games whose reports shall not be downloaded.")

    def handle(self, *args, **options):
        self.options = options
        env.UPDATING.set_value(models.Value.TRUE)
        self.import_associations()
        env.UPDATING.set_value(models.Value.FALSE)

    def import_associations(self):
        for association in models.Association.objects.all():
            self.import_association(association)

    def import_association(self, association):
        if self.options['associations'] and association.bhv_id not in self.options['associations']:
            self.stdout.write('SKIPPING Association: {} (options)'.format(association))
            return

        for district in association.district_set.all():
            self.import_district(district)

    def import_district(self, district):
        if self.options['districts'] and district.bhv_id not in self.options['districts']:
            self.stdout.write('SKIPPING District: {} (options)'.format(district))
            return

        for league in district.league_set.all():
            self.import_league(league)

    def import_league(self, league):
        if self.options['leagues'] and league.bhv_id not in self.options['leagues']:
            self.stdout.write('SKIPPING League: {} (options)'.format(league))
            return

        for game in league.game_set.all():
            self.import_game(game)

    def import_game(self, game):
        Path(settings.REPORTS_PATH).mkdir(parents=True, exist_ok=True)

        if self.options['games'] and game.number not in self.options['games']:
            self.stdout.write('SKIPPING Report: {} - {}(options)'.format(game.report_number, game))
        elif game.report_number is None:
            self.stdout.write('SKIPPING Report: {} - {} (no report)'.format(game.report_number, game))
        elif game.report_path().is_file():
            if not self.options['force_update']:
                self.stdout.write('EXISTING Report: {} - {}'.format(game.report_number, game))
            else:
                self.stdout.write('REDOWNLOADING Report: {} - {}'.format(game.report_number, game))
                self.download_report(game)
        else:
            self.stdout.write('DOWNLOADING Report: {} - {}'.format(game.report_number, game))
            self.download_report(game)

    @staticmethod
    def download_report(game):
        response = requests.get(game.report_url(), stream=True)
        game.report_path().write_bytes(response.content)
