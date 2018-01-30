import re
from urllib.parse import urlsplit, parse_qs

import os

import requests
import tabula
from django.core.management import BaseCommand, CommandError

from base.models import Game, Team, Score, Player


class Command(BaseCommand):

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--game', action='append', metavar='ID', type=str,
                           help='number of a specific game to be imported')
        group.add_argument('--team', action='append', metavar='ID', type=str,
                           help='number of a specific game to be imported')
        group.add_argument('--league', action='append', metavar='ID', type=str,
                           help='number of a specific game to be imported')
        group.add_argument('--district', action='append', metavar='ID', type=str,
                           help='number of a specific game to be imported')
        group.add_argument('--association', action='append', metavar='ID', type=str,
                           help='number of a specific game to be imported')
        parser.add_argument('--force', '-f', action='store_true',
                            help='force download of report and update of scores')

    def handle(self, *args, **options):
        if options['game']:
            for game_id in options['game']:
                try:
                    game = Game.objects.get(pk=game_id)
                    _import_game(game)
                except Game.DoesNotExist:
                    raise CommandError('Game "%s" does not exist' % game_id)
        elif options['league']:
            leagues = options['league']


def _import_association(association_id):
    pass


def _import_district(district_id):
    pass


def _import_game(game):
    pass


def add_scores(table, game, team):
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
        except ValueError:
            continue


def create_game(self, game_row, league):
    report_url = game_row.xpath('./td[11]/a/@href')[0]
    params = urlsplit(report_url).query
    game_id = parse_qs(params)['sGID'][0]
    if Game.objects.filter(number=game_id).exists():
        return

    file_path = os.path.join(self.reports_root, league.district.association.abbreviation, game_id) + '.pdf'
    if not os.path.isfile(file_path):
        response = requests.get(report_url, stream=True)
        with open(file_path, 'wb') as file:
            file.write(response.content)

    teams_pdf = tabula.read_pdf(file_path, output_format='json', **{'pages': 1, 'lattice': True})
    team_names = teams_pdf[0]['data'][3][1]['text']
    home_team_name, guest_team_name = self.parse_team_names(team_names)
    home_team = Team.objects.get_or_create(name=home_team_name, league=league)[0]
    guest_team = Team.objects.get_or_create(name=guest_team_name, league=league)[0]
    if Game.objects.filter(home_team=home_team, guest_team=guest_team).exists():
        return
    game = Game(number=game_id, home_team=home_team, guest_team=guest_team)
    game.save()

    try:
        scores_pdf = tabula.read_pdf(file_path, output_format='json', encoding='cp1252',
                                     **{'pages': 2, 'lattice': True})
    except UnicodeDecodeError:
        self.stdout.write(file_path)
        return

    self.add_scores(scores_pdf[0], game=game, team=home_team)
    self.add_scores(scores_pdf[1], game=game, team=guest_team)


def parse_penalty_data(self, text: str) -> (int, int):
    match = re.match("([0-9]+)/([0-9]+)", text)
    if match:
        return match.group(1), match.group(2)
    return 0, 0


def parse_team_names(self, text: str) -> (int, int):
    match = re.match("(.+) - (.+)", text)
    return match.group(1), match.group(2)
