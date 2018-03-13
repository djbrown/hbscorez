import re
from urllib.parse import urlsplit, parse_qs

import requests
from django.core.management import BaseCommand
from lxml import html

from base import models


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
        # league_abbreviation = game_row[0].text
        number = int(game_row[1].text)

        if self.options['games'] and number not in self.options['games']:
            self.stdout.write('SKIPPING Game: {} (options)'.format(number))
            return

        href = game_row[10][0].get('href')
        query = urlsplit(href).query
        report_number = int(parse_qs(query)['sGID'][0])

        if not models.Game.objects.filter(number=number).exists():
            opening_whistle = models.Game.parse_opening_whistle(game_row[2].text)
            sports_hall = self.import_sports_hall(game_row[3][0])
            home_team_short_name = game_row[4].text
            guest_team_short_name = game_row[6].text
            home_team = models.Team.objects.get(league=league, short_name=home_team_short_name)
            guest_team = models.Team.objects.get(league=league, short_name=guest_team_short_name)
            home_goals = int(game_row[7].text)
            guest_goals = int(game_row[9].text)

            game = models.Game.objects.create(number=number, league=league, opening_whistle=opening_whistle,
                                              sports_hall=sports_hall, home_team=home_team, guest_team=guest_team,
                                              home_goals=home_goals, guest_goals=guest_goals,
                                              report_number=report_number)
            self.stdout.write('CREATING Game: {}'.format(game))

        else:
            game = models.Game.objects.get(number=number)
            if game.report_number != report_number:
                self.stdout.write('UPDATING Game: {} (report_number)'.format(game))
                game.report_number = report_number
                models.Score.objects.filter(game=game).delete()
                game.save()
            else:
                self.stdout.write('EXISTING Game: {}'.format(game))

    def import_sports_hall(self, link):
        number = link.text
        href = link.get('href')
        query = urlsplit(href).query
        bhv_id = int(parse_qs(query)['gymID'][0])

        if not models.SportsHall.objects.filter(number=number, bhv_id=bhv_id).exists():
            url = 'https://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID=1&gymID={}'.format(bhv_id)
            response = requests.get(url)
            tree = html.fromstring(response.text.encode('latin-1').decode())

            table = tree.xpath('//table[@class="gym"]')[0]
            name = table[0][1][0].text
            city = table[1][1].text
            street = table[2][1].text
            address = street + ', ' + city
            phone_number = table[3][1].text

            map_script = tree.xpath('//script')[4].text
            latitude, longitude = re.search("^   new mxn.LatLonPoint\(([.0-9]+),([.0-9]+)\)\),$",
                                            map_script, re.MULTILINE).groups()

            sports_hall = models.SportsHall.objects.create(number=number, name=name, address=address,
                                                           phone_number=phone_number, latitude=latitude,
                                                           longitude=longitude, bhv_id=bhv_id)
            self.stdout.write('CREATING Sports Hall: {}'.format(sports_hall))
            return sports_hall
        else:
            sports_hall = models.SportsHall.objects.get(number=number)
            self.stdout.write('EXISTING Sports Hall: {}'.format(sports_hall))
            return sports_hall
