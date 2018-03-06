from lxml import html
from urllib.parse import urlsplit, parse_qs

import requests
from django.core.management import BaseCommand

from base.models import League, Team, Game, Score


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

            game_rows = tree.xpath("//table[@class='gametable']/tr[position() > 1 and ./td[11]/a[text() = 'PI']/@href]")
            for game_row in game_rows:
                self.create_game(game_row, league)

    def create_game(self, game_row, league):
        report_url = game_row.xpath('./td[11]/a/@href')[0]
        params = urlsplit(report_url).query
        report_number = int(parse_qs(params)['sGID'][0])
        number = game_row[1].text

        if not Game.objects.filter(number=number).exists():
            home_team_short_name = game_row.xpath('td[5]')[0].text
            guest_team_short_name = game_row.xpath('td[7]')[0].text
            home_team = Team.objects.get(league=league, short_name=home_team_short_name)
            guest_team = Team.objects.get(league=league, short_name=guest_team_short_name)

            game = Game.objects.create(number=number, league=league, home_team=home_team,
                                       guest_team=guest_team, report_number=report_number)
            self.stdout.write(' CREATING {}'.format(game))
            game.save()
            return

        else:
            game = Game.objects.get(number=number)
            if game.report_number != report_number:
                self.stdout.write(' UPDATING {} (report_number)'.format(game))
                game.report_number = report_number
                Score.objects.filter(game=game).delete()
                game.save()
                return
            else:
                self.stdout.write(' EXISTING {}'.format(game))
                return
