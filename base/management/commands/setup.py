from django.core.management import BaseCommand
from django.db import transaction

from base import logic
from base import models
from base import parsing
from base import source_url
from base.middleware import env


class Command(BaseCommand):
    options = {}
    processed_districts = set()

    def add_arguments(self, parser):
        parser.add_argument('--youth', action='store_true', help="Include youth teams in setup.")
        parser.add_argument('--associations', '-a', nargs='+', type=int, metavar='orgGrpID',
                            help="IDs of Associations to be setup.")
        parser.add_argument('--districts', '-d', nargs='+', type=int, metavar='orgID',
                            help="IDs of Districts to be setup.")
        parser.add_argument('--leagues', '-l', nargs='+', type=int, metavar='score',
                            help="IDs of Leagues to be setup.")

    def handle(self, *args, **options):
        self.options = options
        env.UPDATING.set_value(models.Value.TRUE)
        self.create_associations()
        env.UPDATING.set_value(models.Value.FALSE)

    def create_associations(self):
        url = source_url.associations_url()
        dom = logic.get_html(url)
        links = dom.xpath('//div[@id="main-content"]/div/ul/li/a')
        for link in links:
            self.create_association(link)

    def create_association(self, association_link):
        name = association_link.text
        abbreviation = logic.get_association_abbreviation(name)
        bhv_id = parsing.parse_association_bhv_id(association_link)

        if self.options['associations'] and bhv_id not in self.options['associations']:
            self.stdout.write('SKIPPING Association (options): {} {}'.format(bhv_id, name))
            return

        association, created = models.Association.objects.get_or_create(name=name, abbreviation=abbreviation,
                                                                        bhv_id=bhv_id)
        if created:
            self.stdout.write('CREATED Association: {}'.format(association))
        else:
            self.stdout.write('EXISTING Association: {}'.format(association))

        url = association.source_url()
        dom = logic.get_html(url)
        items = dom.xpath('//select[@name="orgID"]/option[position()>1]')
        for item in items:
            self.create_district(item, association)

    def create_district(self, district_item, association):
        name = district_item.text
        bhv_id = int(district_item.get('value'))

        if self.options['districts'] and bhv_id not in self.options['districts']:
            self.stdout.write('SKIPPING District (options): {} {}'.format(bhv_id, name))
            return

        district, created = models.District.objects.get_or_create(name=name, bhv_id=bhv_id)
        district.associations.add(association)
        if bhv_id in self.processed_districts:
            self.stdout.write('SKIPPING District: {} {} (already processed)'.format(bhv_id, name))
            return

        if created:
            self.stdout.write('CREATED District: {}'.format(district))
        else:
            self.stdout.write('EXISTING District: {}'.format(district))
        self.processed_districts.add(bhv_id)

        url = district.source_url()
        dom = logic.get_html(url)
        links = dom.xpath('//div[@id="results"]/div/table[2]/tr/td[1]/a')
        for link in links:
            self.create_league(link, district)

    @transaction.atomic
    def create_league(self, league_link, district):
        abbreviation = league_link.text
        bhv_id = parsing.parse_league_bhv_id(league_link)

        if self.options['leagues'] and bhv_id not in self.options['leagues']:
            self.stdout.write('SKIPPING League (options): {} {}'.format(bhv_id, abbreviation))
            return

        if abbreviation[:1] in ['m', 'w', 'g', 'u'] and not self.options['youth']:
            self.stdout.write('SKIPPING League (youth league): {} {}'.format(bhv_id, abbreviation))
            return

        url = source_url.league_source_url(bhv_id)
        dom = logic.get_html(url)

        name = parsing.parse_league_name(dom)

        if logic.is_youth_league(name) and not self.options['youth']:
            self.stdout.write('SKIPPING League (youth league): {} {}'.format(bhv_id, name))
            return

        team_links = dom.xpath('//table[@class="scoretable"]/tr[position() > 1]/td[3]/a') or \
                     dom.xpath('//table[@class="scoretable"]/tr[position() > 1]/td[2]/a')
        if not team_links:
            self.stdout.write('SKIPPING League: {} {} (no team table)'.format(bhv_id, name))
            return

        game_rows = parsing.parse_game_rows(dom)
        if not game_rows:
            self.stdout.write('SKIPPING League (no games): {} {}'.format(bhv_id, name))
            return
        if len(game_rows) < len(team_links) * (len(team_links) - 1):
            self.stdout.write('SKIPPING League (few games): {} {}'.format(bhv_id, abbreviation))
            return

        league, created = models.League.objects.get_or_create(name=name, abbreviation=abbreviation, district=district,
                                                              bhv_id=bhv_id)
        if created:
            self.stdout.write('CREATED League: {}'.format(league))
        else:
            self.stdout.write('EXISTING League: {}'.format(league))

        for team_link in team_links:
            self.create_team(team_link, league)

    def create_team(self, link, league):
        bhv_id = parsing.parse_team_bhv_id(link)
        name = link.text

        url = source_url.team_source_url(league.bhv_id, bhv_id)
        dom = logic.get_html(url)
        game_rows = parsing.parse_game_rows(dom)
        short_team_names = [c.text for game_row in game_rows for c in game_row.xpath('td')[4:7:2]]
        short_team_name = max(set(short_team_names), key=short_team_names.count)

        team, created = models.Team.objects.get_or_create(name=name, short_name=short_team_name, league=league,
                                                          bhv_id=bhv_id)
        if created:
            self.stdout.write('CREATED Team: {}'.format(team))
        else:
            self.stdout.write('EXISTING Team: {}'.format(team))
