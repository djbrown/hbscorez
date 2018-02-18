from lxml import html
from urllib.parse import urlsplit, parse_qs

import requests
from django.core.management import BaseCommand

from base.models import League, Team, Game


class Command(BaseCommand):
    options = {}

    processed_districts = []

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for league in League.objects.all():
            response = requests.get(league.source_url())
            response.encoding = 'utf-8'
            tree = html.fromstring(response.text)

            # todo: game creation has to happen after report was downloaded
            game_rows = tree.xpath("//table[@class='gametable']/tr[position() > 1 and ./td[11]/a[text() = 'PI']/@href]")
            for game_row in game_rows:
                self.create_game(game_row, league)

    def create_game(self, game_row, league):
        report_url = game_row.xpath('./td[11]/a/@href')[0]
        params = urlsplit(report_url).query
        bhv_id = int(parse_qs(params)['sGID'][0])
        number = game_row[1].text
        home_team_short_name = game_row.xpath('td[5]')[0].text
        guest_team_short_name = game_row.xpath('td[7]')[0].text
        home_team = Team.objects.get(league=league, short_name=home_team_short_name)
        guest_team = Team.objects.get(league=league, short_name=guest_team_short_name)
        game, created = Game.objects.get_or_create(number=number, league=league, home_team=home_team,
                                                   guest_team=guest_team, bhv_id=bhv_id)
        if created:
            self.stdout.write(' CREATING {}'.format(game))
        else:
            self.stdout.write(' EXISTING {}'.format(game))
