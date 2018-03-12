from urllib.parse import urlsplit, parse_qs

import requests
from django.core.management import BaseCommand
from lxml import html

from base import models


def get_or_create_sports_hall(text):
    pass


class Command(BaseCommand):
    options = {}

    def add_arguments(self, parser):
        parser.add_argument('--associations', '-a', nargs='+', type=int, metavar='orgGrpID',
                            help="orgGrpIDs of Associations whose games shall be imported.")
        parser.add_argument('--districts', '-d', nargs='+', type=int, metavar='orgID',
                            help="orgIDs of Districts whose games shall be imported.")
        parser.add_argument('--leagues', '-l', nargs='+', type=int, metavar='score',
                            help="sGIDs of Leagues whose games shall be imported.")
        parser.add_argument('--games', '-g', nargs='+', type=int, metavar='game number',
                            help="numbers of Games to be imported.")

    def handle(self, *args, **options):
        self.options = options
        self.import_associations()

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

        response = requests.get(league.source_url())
        response.encoding = 'utf-8'
        tree = html.fromstring(response.text)

        game_rows = tree.xpath("//table[@class='gametable']/tr[position() > 1 and ./td[11]/a[text() = 'PI']/@href]")
        for game_row in game_rows:
            self.import_game(game_row, league)

    def import_game(self, game_row, league):
        league_abbreviation = game_row[0].text
        number = int(game_row[1].text)
        opening_whistle = models.Game.parse_opening_whistle(game_row[2].text)
        sports_hall = get_or_create_sports_hall(game_row[3].text)
        home_team_short_name = game_row[4].text
        guest_team_short_name = game_row[6].text
        home_team = models.Team.objects.get(league=league, short_name=home_team_short_name)
        guest_team = models.Team.objects.get(league=league, short_name=guest_team_short_name)
        home_goals = int(game_row[7].text)
        guest_goals = int(game_row[9].text)
        report_url = game_row.xpath('./td[11]/a/@href')[0]
        params = urlsplit(report_url).query
        report_number = int(parse_qs(params)['sGID'][0])

        if self.options['games'] and number not in self.options['games']:
            self.stdout.write('SKIPPING Game: {} {}:{} (options)'.format(number, home_team, guest_team))
            return

        if not models.Game.objects.filter(number=number).exists():
            game = models.Game.objects.create(number=number,
                                              league=league,
                                              opening_whistle=opening_whistle,
                                              sports_hall=sports_hall,
                                              home_team=home_team,
                                              guest_team=guest_team,
                                              home_goals=home_goals,
                                              guest_goals=guest_goals,
                                              report_number=report_number)
            self.stdout.write('CREATING Game: {}'.format(game))
            return

        else:
            game = models.Game.objects.get(number=number)
            if game.report_number != report_number:
                self.stdout.write('UPDATING Game: {} (report_number)'.format(game))
                game.report_number = report_number
                models.Score.objects.filter(game=game).delete()
                game.save()
                return
            else:
                self.stdout.write('EXISTING Game: {}'.format(game))
                return
