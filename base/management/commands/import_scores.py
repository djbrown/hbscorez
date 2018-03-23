import re

import tabula
from django.core.management import BaseCommand
from django.db import transaction

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
        if self.options['games'] and game.number not in self.options['games']:
            self.stdout.write('SKIPPING Scores: {} - {}(options)'.format(game.report_number, game))
        elif game.report_number is None:
            self.stdout.write('SKIPPING Scores: {} - {} (no report)'.format(game.report_number, game))
        elif not game.report_path().is_file():
            self.stdout.write('SKIPPING Scores: {} - {} (not found)'.format(game.report_number, game))
        elif game.score_set.count() > 0:
            if not self.options['force_update']:
                self.stdout.write('SKIPPING Scores: {} - {} (existing scores)'.format(game.report_number, game))
            else:
                self.stdout.write('REIMPORTING Scores: {} - {}'.format(game.report_number, game))
                models.Score.objects.filter(game=game).delete()
                self.import_scores(game)
        else:
            self.stdout.write('IMPORTING Scores: {} - {}'.format(game.report_number, game))
            self.import_scores(game)

    @transaction.atomic
    def import_scores(self, game):
        path = str(game.report_path())
        scores_pdf = tabula.read_pdf(path, output_format='json', **{'pages': 2, 'lattice': True})

        self.add_scores(scores_pdf[0], game=game, team=game.home_team)
        self.add_scores(scores_pdf[1], game=game, team=game.guest_team)

    def add_scores(self, table, game, team):
        table_rows = table['data']
        for table_row in table_rows[2:]:
            row_data = [cell['text'] for cell in table_row]

            player_number = row_data[0] or None
            player_name = row_data[1]
            # player_year_of_birth = row_data[2]
            try:
                goals = int(row_data[5])
            except ValueError:
                goals = 0
            penalty_tries, penalty_goals = parse_penalty_data(row_data[6])
            warning_time = models.Score.parse_game_time(row_data[7])
            first_suspension_time = models.Score.parse_game_time(row_data[8])
            second_suspension_time = models.Score.parse_game_time(row_data[9])
            third_suspension_time = models.Score.parse_game_time(row_data[10])
            disqualification_time = models.Score.parse_game_time(row_data[11])
            report_time = models.Score.parse_game_time(row_data[12])
            team_suspension_time = models.Score.parse_game_time(row_data[13])

            if not player_name or player_number in ('A', 'B', 'C', 'D'):
                continue

            player, created = models.Player.objects.get_or_create(name=player_name, team=team)
            if created:
                self.stdout.write('CREATED Player: {}'.format(player))

            if models.Score.objects.filter(player=player, game=game).exists():
                self.stdout.write('SKIPPING Score: {} {} (already exists)'.format(player, game))
                continue

            models.Score.objects.create(
                player=player,
                player_number=player_number,
                game=game,
                goals=goals,
                penalty_goals=penalty_goals,
                penalty_tries=penalty_tries,
                warning_time=warning_time,
                first_suspension_time=first_suspension_time,
                second_suspension_time=second_suspension_time,
                third_suspension_time=third_suspension_time,
                disqualification_time=disqualification_time,
                report_time=report_time,
                team_suspension_time=team_suspension_time
            )


def parse_penalty_data(text: str) -> (int, int):
    match = re.match("([0-9]+)/([0-9]+)", text)
    if match:
        return match.group(1), match.group(2)
    return 0, 0


def parse_team_names(text: str) -> (int, int):
    match = re.match("(.+) - (.+)", text)
    return match.group(1), match.group(2)
