import logging
from typing import Any

from django.core.management import BaseCommand

from associations.models import Association
from base import http, logic, parsing
from base.middleware import env
from base.models import Value
from districts.models import District
from leagues.management.commands.import_leagues import add_default_arguments
from leagues.models import League, Season

LOGGER = logging.getLogger('hbscorez')


class Command(BaseCommand):
    options: dict[str, Any] = {}

    def add_arguments(self, parser):
        add_default_arguments(parser)
        parser.add_argument('--games', '-g', nargs='+', type=int, metavar='game number',
                            help="numbers of Games.")

    def handle(self, *args, **options):
        self.options = options
        self.options['processed_sports_halls'] = set()
        env.UPDATING.set_value(Value.TRUE)
        self.import_associations()
        env.UPDATING.set_value(Value.FALSE)

    def import_associations(self):
        for association in Association.objects.all():
            self.import_association(association)

    def import_association(self, association: Association):
        if self.options['associations'] and association.bhv_id not in self.options['associations']:
            LOGGER.debug('SKIPPING Association: %s (options)', association)
            return

        for district in association.district_set.all():
            self.import_district(district)

    def import_district(self, district: District):
        if self.options['districts'] and district.bhv_id not in self.options['districts']:
            LOGGER.debug('SKIPPING District: %s (options)', district)
            return

        season_pks = district.league_set.values('season').distinct()
        seasons = Season.objects.filter(pk__in=season_pks)
        for season in seasons:
            self.import_district_season(district, season)

    def import_district_season(self, district: District, season: Season):
        if self.options['seasons'] and season.start_year not in self.options['seasons']:
            LOGGER.debug('SKIPPING District Season: %s %s (options)', district, season)
            return

        for league in district.league_set.filter(season=season):
            self.import_league(league)

    def import_league(self, league: League):
        if self.options['leagues'] and league.bhv_id not in self.options['leagues']:
            LOGGER.debug('SKIPPING League: %s (options)', league)
            return

        if league.youth and not self.options['youth']:
            LOGGER.debug('SKIPPING League (youth league): %s', league)
            return

        html = http.get_text(league.source_url())
        dom = parsing.html_dom(html)

        game_rows = parsing.parse_game_rows(dom)
        for game_row in game_rows:
            try:
                sports_hall = logic.scrape_sports_hall(game_row, processed=self.options['processed_sports_halls'])
                if sports_hall is not None:
                    self.options['processed_sports_halls'].add(sports_hall.bhv_id)
                logic.scrape_game(game_row, league, sports_hall, self.options['games'])
            except Exception:
                LOGGER.exception("Could not import Game")
