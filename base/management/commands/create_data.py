import os
import re
from urllib.parse import parse_qs, urlsplit

import requests
import tabula
from django.conf import settings
from django.core.management import BaseCommand
from lxml import html

from associations.models import Association
from districts.models import District
from scorers.models import League, Player, Score, Team, Game


class Command(BaseCommand):
    mode = 0
    reports_root = os.path.join(settings.BASE_DIR, "reports")

    def parse_penalty_data(self, text: str) -> (int, int):
        match = re.match("([0-9]+)/([0-9]+)", text)
        if match:
            return match.group(1), match.group(2)
        return 0, 0

    def parse_team_names(self, text: str) -> (int, int):
        match = re.match("(.+) - (.+)", text)
        return match.group(1), match.group(2)

    def add_arguments(self, parser):
        parser.add_argument('--mode', help="0=all, 1=adults, 2=m-vl, 3=game", type=int)
        parser.add_argument('--clean', action="store_true")

    def handle(self, *args, **options):
        self.mode = options.get('mode', 0)
        if options['clean']:
            Score.objects.all().delete()
            Player.objects.all().delete()
            Team.objects.all().delete()
            League.objects.all().delete()
            District.objects.all().delete()
            Association.objects.all().delete()

        os.makedirs(self.reports_root, exist_ok=True)

        associations = [
            ('Badischer Handball-Verband', 'BHV', 'BAD')
            # ('Bayerischer Handball-Verband', 'BHV', 'BAY')
            # ('Südbadischer Handballverband', 'SHV', 'BADSUED')
            # ('Handballverband Württemberg', 'HVW', 'WUERT')
        ]

        for num, association in enumerate(associations):
            if self.mode >= 2 and num != 0:
                continue
            self.create_association(*association)

    def create_association(self, name, acronym, abbreviation):
        association = Association.objects.get_or_create(name=name, acronym=acronym, abbreviation=abbreviation)[0]
        os.makedirs(os.path.join(self.reports_root, abbreviation), exist_ok=True)

        districts = [
            ('Baden-Württemberg Oberliga', 'BWOL', association, 35, 4),
            ('Badischer Handball-Verband', 'BHV', association, 35, 35),
            ('Bezirk Nord', 'NORD', association, 35, 84),
            ('Bezirk Süd', 'SÜD', association, 35, 43),
            ('Bruchsal', 'BR', association, 35, 36),
            ('Heidelberg', 'HD', association, 35, 37),
            ('Karlsruhe', 'KA', association, 35, 38),
            ('Mannheim', 'MA', association, 35, 39),
            ('Pforzheim', 'PF', association, 35, 40),
        ]
        for num, data in enumerate(districts):
            if self.mode >= 2 and num != 1:
                continue
            self.create_district(*data)

    def create_district(self, name, abbreviation, association, group_id, org_id):
        district = District.objects.get_or_create(name=name, abbreviation=abbreviation, association=association)[0]

        url = 'http://spo.handball4all.de/Spielbetrieb/index.php'
        request_data = {
            'orgGrpID': group_id,
            'orgID': org_id,
        }
        response = requests.post(url=url, data=request_data)

        tree = html.fromstring(response.text.encode('latin-1').decode())
        league_links = tree.xpath('//*[@id="results"]/div/table[2]/tr/td[1]/a')

        for num, league_link in enumerate(league_links):
            self.create_league(league_link, district)

    def create_league(self, link, district):
        abbreviation = link.text
        if self.mode > 0 and (abbreviation[:2] == 'mJ' or abbreviation[:2] == 'wJ') or (
                        self.mode > 1 and abbreviation != 'M-VL'):
            return

        url = 'http://spo.handball4all.de/Spielbetrieb/index.php' + link.get('href') + '&all=1'
        response = requests.get(url=url)

        tree = html.fromstring(response.text.encode("latin-1").decode())
        heading = tree.xpath('//*[@id="results"]/div/h1/text()[2]')[0]
        name = heading.split(' - ')[0]

        league = League.objects.get_or_create(name=name, abbreviation=abbreviation, district=district)[0]

        team_links = tree.xpath('//table[@class="scoretable"]/tr[position() > 1]/td[3]/a')

        for team_link in team_links:
            Team.objects.get_or_create(name=team_link.text, league=league)

        game_rows = tree.xpath('//table[@class="gametable"]/tr[position() > 1 and ./td[11]/a/@href]')
        for num, game_row in enumerate(game_rows):
            self.create_game(game_row, league=league)
            if self.mode >= 3:
                break

    def create_game(self, game_row, league):
        report_url = game_row.xpath('./td[11]/a/@href')[0]
        params = urlsplit(report_url)[3]
        game_id = parse_qs(params)['sGID'][0]
        if Game.objects.filter(number=game_id).exists():
            return

        file_path = os.path.join(self.reports_root, league.district.association.abbreviation, game_id) + '.pdf'
        if not os.path.isfile(file_path):
            response = requests.get(report_url, stream=True)
            with open(file_path, 'wb') as file:
                file.write(response.content)

        teams_pdf = tabula.read_pdf(file_path, output_format='json', **{'pages': 1, 'lattice': True})
        team_names = teams_pdf[0]['data'][3][1]['text']
        home_team_name, guest_team_name = self.parse_team_names(team_names)
        home_team = Team.objects.get_or_create(name=home_team_name, league=league)[0]
        guest_team = Team.objects.get_or_create(name=guest_team_name, league=league)[0]
        game = Game(number=game_id, home_team=home_team, guest_team=guest_team)
        game.save()

        scores_pdf = tabula.read_pdf(file_path, output_format='json', encoding='cp1252',
                                     **{'pages': 2, 'lattice': True})
        self.add_scores(scores_pdf[0], game=game, team=home_team)
        self.add_scores(scores_pdf[1], game=game, team=guest_team)

    def add_scores(self, table, game, team):
        table_rows = table['data']
        for table_row in table_rows[2:]:
            row_data = [cell['text'] for cell in table_row]
            player_number = row_data[0]
            player_name = row_data[1].encode("cp1252").decode()
            # player_year_of_birth = row_data[2]
            goals_total = row_data[5] or 0
            penalty_tries, penalty_goals = self.parse_penalty_data(row_data[6])
            # warning_time = row_data[7]
            # first_suspension_time = row_data[8]
            # second_suspension_time = row_data[9]
            # third_suspension_time = row_data[10]
            # disqualification_time = row_data[11]
            # report_time = row_data[12]
            # team_suspension_time = row_data[13]

            if not player_name or player_number in ('A', 'B', 'C', 'D'):
                continue

            player = Player.objects.get_or_create(name=player_name, team=team)[0]

            try:
                score = Score(
                    player=player,
                    game=game,
                    goals=goals_total,
                    penalty_goals=penalty_goals,
                )
                score.save()
            except ValueError:
                continue
