import os
import re
from urllib.parse import urlsplit, parse_qs

import requests
from django.conf import settings
from django.core.management import BaseCommand
from lxml import html

from base.models import *
from hbscorez import settings

association_abbreviations = {
    'Badischer Handball-Verband': 'BHV',
    'Fédération Luxembourgeoise de Handball': 'FLH',
    'Hamburger Handball-Verband': 'HHV',
    'Handball Baden-Württemberg': 'HBW',
    'Handballoberliga Rheinland-Pfalz/Saar': 'RPS',
    'Handballverband Rheinhessen': 'HVR',
    'Handballverband Saar': 'HVS',
    'Handballverband Schleswig-Holstein': 'HVSH',
    'Handballverband Württemberg': 'HVW',
    'Mitteldeutscher Handball-Verband': 'MHV',
    'Oberliga Hamburg - Schleswig-Holstein': 'HHSH',
    'Südbadischer Handballverband': 'SHV',
    'Thüringer Handball-Verband': 'THV',
    'Vorarlberger Handballverband': 'VHV',
}


class Command(BaseCommand):
    include_youth = False

    processed_districts = []

    def add_arguments(self, parser):
        parser.add_argument('--include-youth', action='store_true', help="Include youth teams in setup.")

    def handle(self, *args, **options):
        self.prepare_with_options(**options)
        self.create_associations()

    def prepare_with_options(self, **options):
        self.include_youth = options['include_youth']

    def create_associations(self):
        response = requests.get('https://spo.handball4all.de/')
        tree = html.fromstring(response.text.encode('latin-1').decode())
        association_links = tree.xpath('//div[@id="main-content"]/div/ul/li/a')
        for association_num, association_link in enumerate(association_links, start=1):
            # todo: remove debug condition
            # if association_num != :
            #     continue
            nums = (association_num, len(association_links))
            self.stdout.write('({}/{})'.format(*nums), ending='')
            self.create_association(association_link, nums)

    def create_association(self, association_link, nums):
        name = association_link.text
        abbreviation = association_abbreviations[name]
        href = association_link.get('href')
        query = urlsplit(href).query
        bhv_id = parse_qs(query)['orgGrpID'][0]
        association, created = Association.objects.get_or_create(name=name, abbreviation=abbreviation, bhv_id=bhv_id)
        if created:
            self.stdout.write('\tCREATING\t{}'.format(association))
        else:
            self.stdout.write('\tEXISTING\t{}'.format(association))

        response = requests.get(association.source_url())
        response.encoding = 'utf-8'
        tree = html.fromstring(response.text)
        district_items = tree.xpath('//select[@name="orgID"]/option[position()>1]')
        for district_num, district_item in enumerate(district_items, start=1):
            # todo: remove debug condition
            # if district_num != :
            #     continue
            nnums = (*nums, district_num, len(district_items))
            self.stdout.write('({}/{}) ({}/{})'.format(*nnums), ending='')
            self.create_district(district_item, association, nnums)

    def create_district(self, district_item, association, nums):
        name = district_item.text
        bhv_id = district_item.get('value')
        district, created = District.objects.get_or_create(name=name, bhv_id=bhv_id)
        district.associations.add(association)
        if bhv_id in self.processed_districts:
            self.stdout.write(' SKIPPING (already processed)')
            return
        if created:
            self.stdout.write('\tCREATING\t{}'.format(district))
        else:
            self.stdout.write('\tEXISTING\t{}'.format(district))
        self.processed_districts.append(bhv_id)

        response = requests.get(district.source_url())
        response.encoding = 'utf-8'
        tree = html.fromstring(response.text)
        # league_links = tree.xpath('//div[@id="results"]/div/table[2]/tr[td[2][text() != " "]]/td[1]/a')
        league_links = tree.xpath('//div[@id="results"]/div/table[2]/tr/td[1]/a')
        for league_num, league_link in enumerate(league_links, start=1):
            # todo: remove debug condition
            # if league_num != :
            #     continue
            nnums = (*nums, league_num, len(league_links))
            self.stdout.write('({}/{}) ({}/{}) ({}/{})'.format(*nnums), ending='')
            self.create_league(league_link, district, nnums)

    def create_league(self, link, district, nums):
        href = link.get('href')
        query = urlsplit(href).query
        bhv_id = parse_qs(query)['score'][0]
        url = 'https://spo.handball4all.de/Spielbetrieb/index.php?&orgGrpID=1&all=1&score={}'.format(bhv_id)
        response = requests.get(url)
        response.encoding = 'utf-8'
        tree = html.fromstring(response.text)
        heading = tree.xpath('//*[@id="results"]/div/h1/text()[2]')[0]
        name = heading.split(' - ')[0]
        abbreviation = link.text

        if self.is_youth_league(abbreviation, name) and not self.include_youth:
            self.stdout.write('\tSKIPPING (youth league: {} ({}))'.format(name, abbreviation))
            return

        team_links = tree.xpath('//table[@class="scoretable"]/tr[position() > 1]/td[3]/a')
        if not team_links:
            return

        league, created = League.objects.get_or_create(name=name, abbreviation=abbreviation, district=district,
                                                       bhv_id=bhv_id)
        if created:
            self.stdout.write('\tCREATING\t{}'.format(league))
        else:
            self.stdout.write('\tEXISTING\t{}'.format(league))

        league_dir = os.path.join(settings.BASE_DIR, "reports", str(league.bhv_id))
        os.makedirs(league_dir, exist_ok=True)

        for team_num, team_link in enumerate(team_links, start=1):
            # todo: remove debug condition
            # if team_num != :
            #     continue
            nnums = (*nums, team_num, len(team_links))
            self.stdout.write('({}/{}) ({}/{}) ({}/{}) ({}/{})'.format(*nnums), ending='')
            self.create_team(team_link, league, nnums)

        # todo: game creation has to happen after report was downloaded
        game_rows = tree.xpath('//table[@class="gametable"]/tr[position() > 1 and ./td[11]/a/@href]')
        for game_num, game_row in enumerate(game_rows, start=1):
            # todo: remove debug condition
            # if game_num != :
            #     continue
            nnums = (*nums, game_num, len(game_rows))
            self.stdout.write('({}/{}) ({}/{}) ({}/{}) ({}/{})'.format(*nnums), ending='')
            # self.stdout.write("\t SKIPPING (don't create games)")
            # for cell in game_row:
            # print(cell.text)
            self.create_game(game_row, league)

    @staticmethod
    def is_youth_league(league_abbreviation, league_name):
        return league_abbreviation[:1] in ['m', 'w', 'g', 'u'] \
               or re.search('MJ', league_name) \
               or re.search('WJ', league_name) \
               or re.search('Jugend', league_name) \
               or re.search('Mini', league_name)

    def create_team(self, link, league, nums):
        href = link.get('href')
        query = urlsplit(href).query
        bhv_id = parse_qs(query)['teamID'][0]
        name = link.text

        url = 'https://spo.handball4all.de/Spielbetrieb/index.php' + href
        response = requests.get(url)
        response.encoding = 'utf-8'
        tree = html.fromstring(response.text)
        game_rows = tree.xpath('//table[@class="gametable"]/tr[position() > 1]')
        short_team_names = [c.text for game_row in game_rows for c in game_row.xpath('td')[4:7:2]]
        short_team_name = max(set(short_team_names), key=short_team_names.count)

        team, created = Team.objects.get_or_create(name=name, short_name=short_team_name, league=league, bhv_id=bhv_id)
        if created:
            self.stdout.write('\tCREATING\t{}'.format(team))
        else:
            self.stdout.write('\tEXISTING\t{}'.format(team))

    def create_game(self, game_row, league):
        report_url = game_row.xpath('./td[11]/a/@href')[0]
        params = urlsplit(report_url).query
        bhv_id = parse_qs(params)['sGID'][0]
        number = game_row[1].text
        home_team_short_name = game_row.xpath('td[5]')[0].text
        guest_team_short_name = game_row.xpath('td[7]')[0].text
        home_team = Team.objects.get(league=league, short_name=home_team_short_name)
        guest_team = Team.objects.get(league=league, short_name=guest_team_short_name)
        game, created = Game.objects.get_or_create(number=number, league=league, home_team=home_team,
                                                   guest_team=guest_team, bhv_id=bhv_id)
        if created:
            self.stdout.write('\tCREATING\t{}'.format(game))
        else:
            self.stdout.write('\tEXISTING\t{}'.format(game))
        return

        file_path = os.path.join(reports_root, league.district.association.abbreviation, game_id) + '.pdf'
        if not os.path.isfile(file_path):
            response = requests.get(report_url, stream=True)
            with open(file_path, 'wb') as file:
                file.write(response.content)

        teams_pdf = tabula.read_pdf(file_path, output_format='json', **{'pages': 1, 'lattice': True})
        team_names = teams_pdf[0]['data'][3][1]['text']
        home_team_name, guest_team_name = self.parse_team_names(team_names)
        home_team = Team.objects.get_or_create(name=home_team_name, league=league)[0]
        guest_team = Team.objects.get_or_create(name=guest_team_name, league=league)[0]
        if Game.objects.filter(home_team=home_team, guest_team=guest_team).exists():
            return
        game = Game(number=game_id, home_team=home_team, guest_team=guest_team)
        game.save()

        try:
            scores_pdf = tabula.read_pdf(file_path, output_format='json', encoding='cp1252',
                                         **{'pages': 2, 'lattice': True})
        except UnicodeDecodeError:
            stdout.write(file_path)
            return

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
