import logging
from typing import Dict

from django.core.management import BaseCommand

from associations.models import Association
from base import logic, parsing
from base.middleware import env
from base.models import Value
from games.models import Game
from leagues.models import Season
from players.models import Score
from sports_halls.models import SportsHall
from teams.models import Team

logger = logging.getLogger('hbscorez')


class Command(BaseCommand):
    options: Dict = {}

    def add_arguments(self, parser):
        parser.add_argument('--associations', '-a', nargs='+', type=int, metavar='orgGrpID',
                            help="orgGrpIDs of Associations whose games shall be imported.")
        parser.add_argument('--districts', '-d', nargs='+', type=int, metavar='orgID',
                            help="orgIDs of Districts whose games shall be imported.")
        parser.add_argument('--seasons', '-s', nargs='+', type=int, metavar='start_year',
                            help="Start Years of Seasons to be setup.")
        parser.add_argument('--leagues', '-l', nargs='+', type=int, metavar='score',
                            help="sGIDs of Leagues whose games shall be imported.")
        parser.add_argument('--games', '-g', nargs='+', type=int, metavar='game number',
                            help="numbers of Games to be imported.")

    def handle(self, *args, **options):
        self.options = options
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

        tree = logic.get_html(league.source_url())

        game_rows = tree.xpath("//table[@class='gametable']/tr[position() > 1]")
        for game_row in game_rows:
            self.import_game(game_row, league)

    def import_game(self, game_row, league):
        # league_abbreviation = game_row[0].text
        number = int(game_row[1].text)

        if self.options['games'] and number not in self.options['games']:
            logger.debug('SKIPPING Game: {} (options)'.format(number))
            return

        opening_whistle = parsing.parse_opening_whistle(game_row[2].text)
        sports_hall = self.get_sports_hall(game_row)
        home_team = Team.objects.get(league=league, short_name=game_row[4].text)
        guest_team = Team.objects.get(league=league, short_name=game_row[6].text)
        home_goals, guest_goals = parsing.parse_goals(game_row)
        report_number = parsing.parse_report_number(game_row[10])
        forfeiting_team = parsing.parse_forfeiting_team(game_row[10], home_team, guest_team)

        if not Game.objects.filter(number=number, league__season=league.season).exists():
            logger.debug('CREATING Game: {}'.format(number))
            game = Game.objects.create(number=number, league=league,
                                       opening_whistle=opening_whistle, sports_hall=sports_hall,
                                       home_team=home_team, guest_team=guest_team,
                                       home_goals=home_goals, guest_goals=guest_goals,
                                       report_number=report_number, forfeiting_team=forfeiting_team)
            logger.info('CREATED Game: {}'.format(game))

        else:
            logger.info('EXISTING Game: {} {}'.format(number, league))
            game = Game.objects.get(number=number, league=league)
            if game.opening_whistle != opening_whistle:
                logger.debug('UPDATING Game opening whistle: {}'.format(game))
                game.opening_whistle = opening_whistle
            if game.sports_hall != sports_hall:
                logger.debug('UPDATING Game Sports Hall: {}'.format(game))
                game.sports_hall = sports_hall
            if game.home_goals != home_goals or game.guest_goals != guest_goals:
                logger.debug('UPDATING Game goals: {}'.format(game))
                game.home_goals = home_goals
                game.guest_goals = guest_goals
                Score.objects.filter(game=game).delete()
                logger.debug('DELETED Game Scores: {}'.format(game))
            if game.report_number != report_number:
                logger.debug('UPDATING Game report number: {}'.format(game))
                game.report_number = report_number
                logger.debug('DELETED Game Scores: {}'.format(game))
                Score.objects.filter(game=game).delete()
            if game.forfeiting_team != forfeiting_team:
                logger.debug('UPDATING Game forfeiting team: {}'.format(game))
                game.forfeiting_team = forfeiting_team
            game.save()

    def get_sports_hall(self, game_row):
        if len(game_row[3]) != 1:
            return None
        link = game_row[3][0]
        number = int(link.text)
        bhv_id = parsing.parse_sports_hall_bhv_id(link)

        sports_hall = SportsHall.objects.filter(number=number, bhv_id=bhv_id)
        if sports_hall.exists():
            return sports_hall[0]

        return self.parse_sports_hall(number, bhv_id)

    def parse_sports_hall(self, number, bhv_id):
        url = SportsHall.build_source_url(bhv_id)
        tree = logic.get_html(url)

        table = tree.xpath('//table[@class="gym"]')[0]
        name = table[0][1][0].text
        city = table[1][1].text
        street = table[2][1].text
        address = street + ", " + city if street else city
        phone_number = table[3][1].text

        latitude, longitude = parsing.parse_coordinates(tree)

        sports_hall = SportsHall.objects.create(number=number, name=name, address=address,
                                                phone_number=phone_number, latitude=latitude,
                                                longitude=longitude, bhv_id=bhv_id)
        logger.info('CREATED Sports Hall: {}'.format(sports_hall))
        return sports_hall
