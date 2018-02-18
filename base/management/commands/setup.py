import re
from urllib.parse import urlsplit, parse_qs

import requests
from django.core.management import BaseCommand
from lxml import html

from base.models import *

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
    options = {}

    processed_districts = []

    def add_arguments(self, parser):
        parser.add_argument('--youth', action='store_true', help="Include youth teams in setup.")

        parser.add_argument('--associations', nargs='+', type=int, metavar='orgGrpID',
                            help="orgGrpIDs of Associations to be included in setup.")

    def handle(self, *args, **options):
        self.options = options
        self.create_associations()

    def create_associations(self):
        response = requests.get('https://spo.handball4all.de/')
        tree = html.fromstring(response.text.encode('latin-1').decode())
        association_links = tree.xpath('//div[@id="main-content"]/div/ul/li/a')
        for association_num, association_link in enumerate(association_links, start=1):
            nums = (association_num, len(association_links))
            self.stdout.write('({:2}/{:2})'.format(*nums), ending='')
            self.create_association(association_link, nums)

    def create_association(self, association_link, nums):
        name = association_link.text
        abbreviation = association_abbreviations[name]
        href = association_link.get('href')
        query = urlsplit(href).query
        bhv_id = int(parse_qs(query)['orgGrpID'][0])

        if self.options['associations'] and bhv_id not in self.options['associations']:
            self.stdout.write(' SKIPPING Association: {:2} {} (options)'.format(bhv_id, name))
            return

        association, created = Association.objects.get_or_create(name=name, abbreviation=abbreviation, bhv_id=bhv_id)
        if created:
            self.stdout.write(' CREATING {}'.format(association))
        else:
            self.stdout.write(' EXISTING {}'.format(association))

        response = requests.get(association.source_url())
        response.encoding = 'utf-8'
        tree = html.fromstring(response.text)
        district_items = tree.xpath('//select[@name="orgID"]/option[position()>1]')
        for district_num, district_item in enumerate(district_items, start=1):
            nnums = (*nums, district_num, len(district_items))
            self.stdout.write('({:2}/{:2}) ({:2}/{:2})'.format(*nnums), ending='')
            self.create_district(district_item, association, nnums)

    def create_district(self, district_item, association, nums):
        name = district_item.text
        bhv_id = int(district_item.get('value'))

        district, created = District.objects.get_or_create(name=name, bhv_id=bhv_id)
        district.associations.add(association)

        if bhv_id in self.processed_districts:
            self.stdout.write(' SKIPPING District: {:2} {} (already processed)'.format(bhv_id, name))
            return

        if created:
            self.stdout.write(' CREATING {}'.format(district))
        else:
            self.stdout.write(' EXISTING {}'.format(district))
        self.processed_districts.append(bhv_id)

        response = requests.get(district.source_url())
        response.encoding = 'utf-8'
        tree = html.fromstring(response.text)
        league_links = tree.xpath('//div[@id="results"]/div/table[2]/tr/td[1]/a')
        for league_num, league_link in enumerate(league_links, start=1):
            nnums = (*nums, league_num, len(league_links))
            self.stdout.write('({:2}/{:2}) ({:2}/{:2}) ({:2}/{:2})'.format(*nnums), ending='')
            self.create_league(league_link, district, nnums)

    def create_league(self, link, district, nums):
        href = link.get('href')
        query = urlsplit(href).query
        bhv_id = int(parse_qs(query)['score'][0])
        url = 'https://spo.handball4all.de/Spielbetrieb/index.php?&orgGrpID=1&all=1&score={}'.format(bhv_id)
        response = requests.get(url)
        response.encoding = 'utf-8'
        tree = html.fromstring(response.text)
        heading = tree.xpath('//*[@id="results"]/div/h1/text()[2]')[0]
        name = heading.split(' - ')[0]
        abbreviation = link.text

        if self.is_youth_league(abbreviation, name) and not self.options['youth']:
            self.stdout.write(' SKIPPING League: {:5} {} (youth league)'.format(bhv_id, name))
            return

        team_links = tree.xpath('//table[@class="scoretable"]/tr[position() > 1]/td[3]/a')
        if not team_links:
            self.stdout.write(' SKIPPING League: {:5} {} (no team table)'.format(bhv_id, name))
            return

        league, created = League.objects.get_or_create(name=name, abbreviation=abbreviation, district=district,
                                                       bhv_id=bhv_id)
        if created:
            self.stdout.write(' CREATING {}'.format(league))
        else:
            self.stdout.write(' EXISTING {}'.format(league))

        for team_num, team_link in enumerate(team_links, start=1):
            nnums = (*nums, team_num, len(team_links))
            self.stdout.write('({:2}/{:2}) ({:2}/{:2}) ({:2}/{:2}) ({:2}/{:2})'.format(*nnums), ending='')
            self.create_team(team_link, league, nnums)

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
        bhv_id = int(parse_qs(query)['teamID'][0])
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
            self.stdout.write(' CREATING {}'.format(team))
        else:
            self.stdout.write(' EXISTING {}'.format(team))
