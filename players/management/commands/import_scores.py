import logging
import os
from typing import Any, Dict

import requests
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

logger = logging.getLogger('hbscorez')


class Command(BaseCommand):
    options: Dict[str, Any] = {}
    bugged_reports = [450001, 473097, 497475, 501159, 546059, 562543, 567811, 572051, 598812, 627428, 638260]

    def add_arguments(self, parser):
        parser.add_argument('--force-update', '-f', action='store_true',
                            help='force download and overwrite if report already exists')
        parser.add_argument('--associations', '-a', nargs='+', type=int, metavar='orgGrpID',
                            help="orgGrpIDs of Associations whose games reports shall be downloaded.")
        parser.add_argument('--districts', '-d', nargs='+', type=int, metavar='orgID',
                            help="orgIDs of Districts whose games reports shall be downloaded.")
        parser.add_argument('--seasons', '-s', nargs='+', type=int, metavar='start_year',
                            help="Start Years of Seasons to be setup.")
        parser.add_argument('--leagues', '-l', nargs='+', type=int, metavar='score',
                            help="sGIDs of Leagues whose games reports shall be downloaded.")
        parser.add_argument('--games', '-g', nargs='+', type=int, metavar='game number',
                            help="numbers of Games whose reports shall be downloaded.")
        parser.add_argument('--skip-games', '-G', nargs='+', type=int, metavar='game number',
                            help="numbers of Games whose reports shall not be downloaded.")

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
            logger.debug('SKIPPING Association: {} (options)'.format(association))
            return

        for district in association.district_set.all():
            self.import_district(district)

    def import_district(self, district):
        if self.options['districts'] and district.bhv_id not in self.options['districts']:
            logger.debug('SKIPPING District: {} (options)'.format(district))
            return

        season_pks = district.league_set.values('season').distinct()
        seasons = Season.objects.filter(pk__in=season_pks)
        for season in seasons:
            self.import_district_season(district, season)

    def import_district_season(self, district, season):
        if self.options['seasons'] and season.start_year not in self.options['seasons']:
            logger.debug('SKIPPING District Season: {} {} (options)'.format(district, season))
            return

        for league in district.league_set.filter(season=season):
            self.import_league(league)

    def import_league(self, league):
        if self.options['leagues'] and league.bhv_id not in self.options['leagues']:
            logger.debug('SKIPPING League: {} (options)'.format(league))
            return

        for game in league.game_set.all():
            self.import_game(game)

    def import_game(self, game: Game):
        if self.options['games'] and game.number not in self.options['games']:
            logger.debug('SKIPPING Game (options): {} - {}'.format(game.report_number, game))
        elif game.report_number is None:
            logger.debug('SKIPPING Game (no report): {} - {}'.format(game.report_number, game))
        elif game.report_number in self.bugged_reports:
            logger.debug('SKIPPING Report (ignore list): {} - {}'.format(game.report_number, game))
        elif game.score_set.count() > 0:
            if not self.options['force_update']:
                logger.debug('SKIPPING Game (existing scores): {} - {}'.format(game.report_number, game))
            else:
                logger.info('REIMPORTING Scores: {} - {}'.format(game.report_number, game))
                game.score_set.delete()
                self.import_scores(game)
        elif game.forfeiting_team is not None:
            logger.debug('SKIPPING Game (forfeit): {} - {}'.format(game.report_number, game))
        else:
            logger.info('IMPORTING Scores: {} - {}'.format(game.report_number, game))
            self.import_scores(game)

    @transaction.atomic
    def import_scores(self, game):
        response = requests.get(game.report_source_url(), stream=True)
        if int(response.headers.get('Content-Length', default=-1)) == 0:
            logger.warning('SKIPPING Scores (empty report file): {} - {}'.format(game.report_number, game))
            return

        game.report_path().write_bytes(response.content)
        path = str(game.report_path())
        scores_pdf = tabula.read_pdf(path, output_format='json', **{'pages': 2, 'lattice': True})

        self.add_scores(scores_pdf[0], game=game, team=game.home_team)
        self.add_scores(scores_pdf[1], game=game, team=game.guest_team)

        os.remove(path)

    def add_scores(self, table, game, team):
        table_rows = table['data']
        for table_row in table_rows[2:]:
            row_data = [cell['text'] for cell in table_row]

            player_number: str = row_data[0]
            player_name: str = row_data[1]
            # player_year_of_birth = row_data[2]

            if not player_number and not player_name:
                return
            if player_number in ('A', 'B', 'C', 'D'):
                logger.debug('SKIPPING Score (coach): {} - {}'.format(player_number, player_name))
                return
            if not player_number:
                logger.warn('SKIPPING Score (no player number): {}'.format(player_name))
                return
            if not player_name:
                logger.warn('SKIPPING Score (no player name): {}'.format(player_number))
                return
            try:
                int(player_number)
            except ValueError as e:
                logger.exception(
                    'invalid Score (invalid player number): {} - {}\n{}'.format(player_number, player_name, e))
                return

            player = Player(name=player_name, team=team)
            score = self.parse_score(player, game, row_data)
            logic.add_score(score)

    def parse_score(self, player: Player, game: Game, row_data)->Score:
        player_number = int(row_data[0])
        goals_str = row_data[5]
        if goals_str == '':
            goals = 0
        else:
            try:
                goals = int(goals_str)
            except ValueError as e:
                goals = 0
                logger.exception('invalid Score goals: {} - {} - {}\n{}'.format(player_number, player.name, goals, e))
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
