import logging
import os
from pathlib import Path
from typing import Any, Dict

import tabula
from django.conf import settings
from django.core.management import BaseCommand
from django.db import transaction

from associations.models import Association
from base import logic, parsing
from base.middleware import env
from base.models import Value
from games.models import Game
from leagues.models import Season
from players.models import Player, Score
from teams.models import Team

from . import parse_report
from .fetch_report import fetch_report

LOGGER = logging.getLogger('hbscorez')


class Command(BaseCommand):
    options: Dict[str, Any] = {}
    bugged_reports = [
        450001, 473097, 497475, 501159, 546059, 562543, 567811, 572051, 598812, 627428, 638260,  # 2018
        893364, 891069, 995291, 1162366,  # 2019
    ]
    bugged_associations = [78]

    def add_arguments(self, parser):
        parser.add_argument('--associations', '-a', nargs='+', type=int, metavar='orgGrpID',
                            help="IDs of Associations.")
        parser.add_argument('--districts', '-d', nargs='+', type=int, metavar='orgID',
                            help="IDs of Districts.")
        parser.add_argument('--seasons', '-s', nargs='+', type=int, metavar='start year',
                            help="Start Years of Seasons.")
        parser.add_argument('--leagues', '-l', nargs='+', type=int, metavar='score/sGID',
                            help="IDs of Leagues.")
        parser.add_argument('--youth', action='store_true',
                            help="Include youth leagues.")
        parser.add_argument('--games', '-g', nargs='+', type=int, metavar='game number',
                            help="numbers of Games.")
        parser.add_argument('--skip-games', '-G', nargs='+', type=int, metavar='game number',
                            help="numbers of Games.")
        parser.add_argument('--force-update', '-f', action='store_true',
                            help='force download and overwrite if report already exists')

    def handle(self, *args, **options):
        self.options = options
        os.makedirs(settings.REPORTS_PATH, exist_ok=True)
        env.UPDATING.set_value(Value.TRUE)
        self.import_associations()
        env.UPDATING.set_value(Value.FALSE)

    def import_associations(self):
        for association in Association.objects.all():
            self.import_association(association)

    def import_association(self, association):
        if self.options['associations'] and association.bhv_id not in self.options['associations']:
            LOGGER.debug('SKIPPING Association: %s (options)', association)
            return

        if association.bhv_id in self.bugged_associations:
            LOGGER.debug('SKIPPING Association (ignore list): %s', association)
            return

        for district in association.district_set.all():
            self.import_district(district)

    def import_district(self, district):
        if self.options['districts'] and district.bhv_id not in self.options['districts']:
            LOGGER.debug('SKIPPING District: %s (options)', district)
            return

        season_pks = district.league_set.values('season').distinct()
        seasons = Season.objects.filter(pk__in=season_pks)
        for season in seasons:
            self.import_district_season(district, season)

    def import_district_season(self, district, season):
        if self.options['seasons'] and season.start_year not in self.options['seasons']:
            LOGGER.debug('SKIPPING District Season: %s %s (options)', district, season)
            return

        for league in district.league_set.filter(season=season):
            self.import_league(league)

    def import_league(self, league):
        if self.options['leagues'] and league.bhv_id not in self.options['leagues']:
            LOGGER.debug('SKIPPING League: %s (options)', league)
            return

        if league.youth and not self.options['youth']:
            LOGGER.debug('SKIPPING League (youth league): %s', league)
            return

        for game in league.game_set.all():
            self.import_game(game)

    def import_game(self, game: Game):
        if self.options['games'] and game.number not in self.options['games']:
            LOGGER.debug('SKIPPING Game (options): %s - %s', game.report_number, game)
        elif game.report_number is None:
            LOGGER.debug('SKIPPING Game (no report): %s - %s', game.report_number, game)
        elif game.report_number in self.bugged_reports:
            LOGGER.debug('SKIPPING Report (ignore list): %s - %s', game.report_number, game)
        elif game.home_team.retirement is not None or game.guest_team.retirement is not None:
            if game.score_set.count() > 0:
                LOGGER.info('DELETING Game Scores (retired team): %s - %s', game.report_number, game)
                game.score_set.all().delete()
            else:
                LOGGER.debug('SKIPPING Game (retired team): %s - %s', game.report_number, game)
        elif game.score_set.count() > 0:
            if not self.options['force_update']:
                LOGGER.debug('SKIPPING Game (existing scores): %s - %s', game.report_number, game)
            else:
                LOGGER.info('REIMPORTING Report: %s - %s', game.report_number, game)
                game.score_set.all().delete()
                import_game(game)
        elif game.forfeiting_team is not None:
            LOGGER.debug('SKIPPING Game (forfeit): %s - %s', game.report_number, game)
        else:
            LOGGER.info('IMPORTING Report: %s - %s', game.report_number, game)
            import_game(game)


@transaction.atomic
def import_game(game: Game):
    path = Path(settings.REPORTS_PATH).joinpath(str(game.report_number) + '.pdf')
    download_report(game, path)
    import_report(game, str(path))
    os.remove(path)


def download_report(game: Game, path: Path):
    response = fetch_report(game)
    if int(response.headers.get('Content-Length', default=-1)) == 0:
        LOGGER.warning('SKIPPING Report (empty file): %s - %s', game.report_number, game)
        return

    path.write_bytes(response.content)


def import_report(game: Game, path: str):
    tables = tabula.read_pdf(path, output_format='json', **{'pages': [1, 2], 'lattice': True})

    game.spectators = parse_report.parse_spectators(tables[0])
    game.save()

    import_scores(tables[2], game=game, team=game.home_team)
    import_scores(tables[3], game=game, team=game.guest_team)


def import_scores(table, game: Game, team: Team):
    table_rows = table['data']
    for table_row in table_rows[2:]:
        row_data = [cell['text'] for cell in table_row]

        player_number: str = row_data[0]
        player_name: str = row_data[1]
        # player_year_of_birth = row_data[2]

        if not player_number and not player_name:
            return
        if player_number in ('A', 'B', 'C', 'D'):
            LOGGER.debug('SKIPPING Score (coach): %s - %s', player_number, player_name)
            return
        if not player_number:
            LOGGER.warning('SKIPPING Score (no player number): %s', player_name)
            return
        if not player_name:
            LOGGER.warning('SKIPPING Score (no player name): %s', player_number)
            return
        try:
            int(player_number)
        except ValueError as err:
            LOGGER.exception('invalid Score (invalid player number): %s - %s\n%s', player_number, player_name, err)
            return

        player = Player(name=player_name, team=team)
        score = parse_score(player, game, row_data)
        logic.add_score(score)


def parse_score(player: Player, game: Game, row_data) -> Score:
    player_number = int(row_data[0])
    goals_str = row_data[5]
    if goals_str == '':
        goals = 0
    else:
        try:
            goals = int(goals_str)
        except ValueError as err:
            goals = 0
            LOGGER.exception('invalid Score goals: %s - %s - %s\n%s', player_number, player.name, goals, err)
    penalty_tries, penalty_goals = parsing.parse_penalty_data(row_data[6])

    return Score(player=player, player_number=int(row_data[0]), game=game, goals=goals,
                 penalty_tries=penalty_tries, penalty_goals=penalty_goals,
                 warning_time=parsing.parse_game_time(row_data[7]),
                 first_suspension_time=parsing.parse_game_time(row_data[8]),
                 second_suspension_time=parsing.parse_game_time(row_data[9]),
                 third_suspension_time=parsing.parse_game_time(row_data[10]),
                 disqualification_time=parsing.parse_game_time(row_data[11]),
                 report_time=parsing.parse_game_time(row_data[12]),
                 team_suspension_time=parsing.parse_game_time(row_data[13]))
