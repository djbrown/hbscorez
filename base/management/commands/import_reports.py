import os
import re

import requests
import tabula
from django.conf import settings
from django.core.management import BaseCommand

from base.models import Game, Score, Player


class Command(BaseCommand):
    reports_root_path = os.path.join(settings.BASE_DIR, 'reports')
    options = {}

    def add_arguments(self, parser):
        parser.add_argument('--force-update', '-f', action='store_true',
                            help='force download of report and update of scores')

    def handle(self, *args, **options):
        self.stdout.write('Downloading Reports...')
        self.options = options
        for game in Game.objects.all():
            if options['force_update']:
                self.delete_reports()
            Score.objects.all().delete()
            self.import_report(game)

    def delete_report(self):
        self.stdout.write('Deleting Reports...')
        # todo: implement deletion of reports

    def import_report(self, game):
        self.stdout.write('Downloading Report {}'.format(game.bhv_id))
        report_path = os.path.join(self.reports_root_path, str(game.bhv_id)) + '.pdf'
        if self.options['force_update'] or not os.path.isfile(report_path):
            response = requests.get(game.report_url(), stream=True)
            with open(report_path, 'wb') as file:
                file.write(response.content)

        teams_pdf = tabula.read_pdf(report_path, output_format='json', **{'pages': 1, 'lattice': True})
        self.stdout.write(' IMPORTING {}'.format(game))

        try:
            scores_pdf = tabula.read_pdf(report_path, output_format='json', encoding='cp1252',
                                         **{'pages': 2, 'lattice': True})
        except UnicodeDecodeError as err:
            self.stdout.write('UnicodeDecodeError on {}\n{}'.format(report_path, err))
            return

        self.add_scores(scores_pdf[0], game=game, team=game.home_team)
        self.add_scores(scores_pdf[1], game=game, team=game.guest_team)

    def add_scores(self, table, game, team):
        table_rows = table['data']
        for table_row in table_rows[2:]:
            row_data = [cell['text'] for cell in table_row]
            player_number = row_data[0]
            player_name = row_data[1].encode("cp1252").decode()
            # player_year_of_birth = row_data[2]
            goals_total = row_data[5] or 0
            penalty_tries, penalty_goals = parse_penalty_data(row_data[6])
            # warning_time = row_data[7]
            # first_suspension_time = row_data[8]
            # second_suspension_time = row_data[9]
            # third_suspension_time = row_data[10]
            # disqualification_time = row_data[11]
            # report_time = row_data[12]
            # team_suspension_time = row_data[13]

            if not player_name or player_number in ('A', 'B', 'C', 'D'):
                continue

            player = Player.objects.get_or_create(name=player_name, team=team)[0]

            try:
                score = Score(
                    player=player,
                    game=game,
                    goals=goals_total,
                    penalty_goals=penalty_goals,
                )
                score.save()
            except ValueError as err:
                self.stdout.write(
                    'UnicodeDecodeError on Game {} Team {} Player {} {}\n{}'.format(game.bhv_id, team.name, player.name,
                                                                                    player_number, err))
                continue


def parse_penalty_data(text: str) -> (int, int):
    match = re.match("([0-9]+)/([0-9]+)", text)
    if match:
        return match.group(1), match.group(2)
    return 0, 0


def parse_team_names(text: str) -> (int, int):
    match = re.match("(.+) - (.+)", text)
    return match.group(1), match.group(2)
