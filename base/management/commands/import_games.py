import re

import requests
from django.core.management import BaseCommand
from lxml import html

from base import models
from base.middleware import env


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
        env.UPDATING.set_value(models.Value.TRUE)
        self.import_associations()
        env.UPDATING.set_value(models.Value.TRUE)

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

        game_rows = tree.xpath("//table[@class='gametable']/tr[position() > 1]")
        for game_row in game_rows:
            self.import_game(game_row, league)

    def parse_goals(self, game_row) -> (int, int):
        home_goals = int(game_row[7].text) if game_row[7].text else None
        guest_goals = int(game_row[9].text) if game_row[9].text else None

        if home_goals is None and guest_goals is None and len(game_row[10]) == 1:
            title = game_row[10][0].get("title", "")
            match = re.match("SpA\((\d+):(\d+)\)", title)
            if match:
                home_goals = match.group(1)
                guest_goals = match.group(2)

        return home_goals, guest_goals

    def import_game(self, game_row, league):
        # league_abbreviation = game_row[0].text
        number = int(game_row[1].text)

        if self.options['games'] and number not in self.options['games']:
            self.stdout.write('SKIPPING Game: {} (options)'.format(number))
            return

        report_number = models.Game.parse_report_number(game_row[10])
        opening_whistle = models.Game.parse_opening_whistle(game_row[2].text)
        sports_hall = self.import_sports_hall(game_row)

        if not models.Game.objects.filter(number=number).exists():
            self.stdout.write('CREATING Game: {}'.format(number))
            home_team_short_name = game_row[4].text
            guest_team_short_name = game_row[6].text
            home_team = models.Team.objects.get(league=league, short_name=home_team_short_name)
            guest_team = models.Team.objects.get(league=league, short_name=guest_team_short_name)
            home_goals, guest_goals = self.parse_goals(game_row)
            forfeiting_team = models.Game.parse_forfeiting_team(game_row[10], home_team, guest_team)

            game = models.Game.objects.create(number=number, league=league,
                                              opening_whistle=opening_whistle, sports_hall=sports_hall,
                                              home_team=home_team, guest_team=guest_team,
                                              home_goals=home_goals, guest_goals=guest_goals,
                                              report_number=report_number, forfeiting_team=forfeiting_team)
            self.stdout.write('CREATED Game: {}'.format(game))

        else:
            self.stdout.write('EXISTING Game: {}'.format(number))
            game = models.Game.objects.get(number=number)
            if game.report_number != report_number:
                self.stdout.write('UPDATING Game Report: {}'.format(game))
                game.report_number = report_number
                self.stdout.write('DELETING Game Scores: {}'.format(game))
                models.Score.objects.filter(game=game).delete()
            if game.sports_hall != sports_hall:
                self.stdout.write('UPDATING Game Sports Hall: {}'.format(game))
                game.sports_hall = sports_hall
                models.Score.objects.filter(game=game).delete()
            game.save()

    def import_sports_hall(self, game_row):
        if len(game_row[3]) != 1:
            return
        link = game_row[3][0]
        number = link.text
        bhv_id = models.SportsHall.parse_bhv_id(link)

        if not models.SportsHall.objects.filter(number=number, bhv_id=bhv_id).exists():
            self.stdout.write('CREATING Sports Hall: {} ({})'.format(number, bhv_id))
            url = 'https://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID=1&gymID={}'.format(bhv_id)
            response = requests.get(url)
            tree = html.fromstring(response.text.encode('latin-1').decode())

            table = tree.xpath('//table[@class="gym"]')[0]
            name = table[0][1][0].text
            city = table[1][1].text
            street = table[2][1].text
            address = street + ", " + city if street else city
            phone_number = table[3][1].text

            map_script = tree.xpath('//script')[4].text
            latitude, longitude = re.search("^   new mxn.LatLonPoint\(([.0-9]+),([.0-9]+)\)\),$",
                                            map_script, re.MULTILINE).groups()

            sports_hall = models.SportsHall.objects.create(number=number, name=name, address=address,
                                                           phone_number=phone_number, latitude=latitude,
                                                           longitude=longitude, bhv_id=bhv_id)
            self.stdout.write('CREATED Sports Hall: {}'.format(sports_hall))
            return sports_hall
        else:
            return models.SportsHall.objects.get(number=number)
