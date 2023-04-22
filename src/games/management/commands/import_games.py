import logging
from typing import Any

from django.core.management import BaseCommand

from associations.models import Association
from base import http, parsing
from base.middleware import env
from base.models import Value
from districts.models import District
from games.models import Game
from leagues.management.commands.setup import add_default_arguments
from leagues.models import League, Season
from players.models import Score
from sports_halls.models import SportsHall
from teams.models import Team

LOGGER = logging.getLogger('hbscorez')


class Command(BaseCommand):
    options: dict[str, Any] = {}

    def add_arguments(self, parser):
        add_default_arguments(parser)
        parser.add_argument('--games', '-g', nargs='+', type=int, metavar='game number',
                            help="numbers of Games.")

    def handle(self, *args, **options):
        self.options = options
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
                self.import_game(game_row, league)
            except Exception:
                logging.getLogger('mail').exception("Could not import Game")

    def import_game(self, game_row, league: League):

        if game_row[1].text == 'Nr.':
            LOGGER.debug('SKIPPING Row (heading)')
            return

        number = int(game_row[1].text)

        if self.options['games'] and number not in self.options['games']:
            LOGGER.debug('SKIPPING Game (options): %s', number)
            return

        opening_whistle = parsing.parse_opening_whistle(game_row[2].text)
        sports_hall = scrape_sports_hall(game_row)
        home_team = Team.objects.get(league=league, short_name=game_row[4].text)
        guest_team = Team.objects.get(league=league, short_name=game_row[6].text)
        home_goals, guest_goals = parsing.parse_goals(game_row)
        report_number = parsing.parse_report_number(game_row[10])
        forfeiting_team = parsing.parse_forfeiting_team(game_row[10], home_team, guest_team)

        if not Game.objects.filter(number=number, league__season=league.season).exists():
            LOGGER.debug('CREATING Game: %s', number)
            game = Game.objects.create(number=number, league=league,
                                       opening_whistle=opening_whistle, sports_hall=sports_hall,
                                       home_team=home_team, guest_team=guest_team,
                                       home_goals=home_goals, guest_goals=guest_goals,
                                       report_number=report_number, forfeiting_team=forfeiting_team)
            LOGGER.info('CREATED Game: %s', game)

        else:
            LOGGER.info('EXISTING Game: %s %s', number, league)
            game = Game.objects.get(number=number, league=league)
            if game.opening_whistle != opening_whistle:
                LOGGER.debug('UPDATING Game opening whistle: %s', game)
                game.opening_whistle = opening_whistle
            if game.sports_hall != sports_hall:
                LOGGER.debug('UPDATING Game Sports Hall: %s', game)
                game.sports_hall = sports_hall
            if game.home_goals != home_goals or game.guest_goals != guest_goals:
                LOGGER.debug('UPDATING Game goals: %s', game)
                game.home_goals = home_goals
                game.guest_goals = guest_goals
                Score.objects.filter(game=game).delete()
                LOGGER.debug('DELETED Game Scores: %s', game)
            if game.report_number != report_number:
                LOGGER.debug('UPDATING Game report number: %s', game)
                game.report_number = report_number
                LOGGER.debug('DELETED Game Scores: %s', game)
                Score.objects.filter(game=game).delete()
            if game.forfeiting_team != forfeiting_team:
                LOGGER.debug('UPDATING Game forfeiting team: %s', game)
                game.forfeiting_team = forfeiting_team
            game.save()


def scrape_sports_hall(game_row):
    if len(game_row[3]) != 1:
        return None
    link = game_row[3][0]
    number = int(link.text)
    bhv_id = parsing.parse_sports_hall_bhv_id(link)

    sports_hall = SportsHall.objects.filter(number=number, bhv_id=bhv_id)
    if sports_hall.exists():
        return sports_hall[0]

    url = SportsHall.build_source_url(bhv_id)
    html = http.get_text(url)
    dom = parsing.html_dom(html)

    sports_hall = parsing.parse_sports_hall(dom)
    sports_hall.bhv_id = bhv_id
    sports_hall.number = number
    sports_hall.save()

    LOGGER.info('CREATED Sports Hall: %s', sports_hall)
    return sports_hall
