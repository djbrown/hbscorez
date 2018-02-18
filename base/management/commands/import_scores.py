import re

import tabula
from django.core.management import BaseCommand

from base.management.common import report_path, find_games
from base.models import Score, Player


class Command(BaseCommand):
    options = {}

    def add_arguments(self, parser):
        parser.add_argument('--games', '-g', nargs='+', type=int, metavar='sGID',
                            help="sGIDs of games whose scores are to be imported.")
        parser.add_argument('--force-update', '-f', action='store_true',
                            help='force download of report and update of scores')

    def handle(self, *args, **options):
        self.options = options
        for game in find_games(options['games']):
            if not report_path(game).is_file():
                self.stdout.write('SKIPPING Scores for {} (not found)'.format(game))
            elif game.score_set.count() == 0:
                self.stdout.write('IMPORTING Scores for {}'.format(game))
                self.import_scores(game)
            elif self.options['force_update']:
                self.stdout.write('REIMPORTING Scores for {}'.format(game))
                Score.object.filter(game=game).delete()
                self.import_scores(game)
            else:
                self.stdout.write('EXISTING Scores for {}'.format(game))

    def import_scores(self, game):
        try:
            path = str(report_path(game))
            scores_pdf = tabula.read_pdf(path, output_format='json', encoding='cp1252',
                                         **{'pages': 2, 'lattice': True})
        except UnicodeDecodeError as err:
            self.stdout.write('UnicodeDecodeError on {}\n{}'.format(game.bhv_id, err))
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
