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
        parser.add_argument('--league_seasons', '-l', nargs='+', type=int, metavar='score',
                            help="IDs of League Seasons to be setup.")

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
            self.create_district_seasons(item, association)

    def create_district_seasons(self, district_item, association):
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

        district_seasons_url = source_url.district_url(district.bhv_id, '2000-01-01')
        district_seasons_dom = logic.get_html(district_seasons_url)
        district_season_headings = district_seasons_dom.xpath('//div[@id="results"]/div/a[@name]/h4')
        district_season_links = district_seasons_dom.xpath('//div[@id="results"]/div/a[@href]')
        district_seasons = zip(district_season_headings, district_season_links)
        for district_season_heading, district_season_link in district_seasons:
            self.create_district_season(district_season_heading, district_season_link, district)

    def create_district_season(self, district_season_heading, district_season_link, district):
        year = parsing.parse_district_season_year(district_season_heading)

        if year < 20110:
            self.stdout.write('SKIPPING District Season (pre 2010): {} {}'.format(district, district_season_link.text))

        if district_season_heading.text.startswith('Sommer'):
            self.stdout.write(
                'SKIPPING District Season (summer season): {} {}'.format(district, district_season_link.text))

        season, season_created = models.Season.objects.get_or_create(year=year)
        if season_created:
            self.stdout.write('CREATED Season: {}'.format(season))
        else:
            self.stdout.write('EXISTING Season: {}'.format(season))

        date = parsing.parse_district_link_date(district_season_link)
        url = source_url.district_url(district.bhv_id, date)
        dom = logic.get_html(url)
        league_season_links = dom.xpath('//div[@id="results"]/div/table[2]/tr/td[1]/a')
        for league_season_link in league_season_links:
            self.create_league_season(league_season_link, district, season)

    @transaction.atomic
    def create_league_season(self, league_season_link, district, season):
        abbreviation = league_season_link.text
        bhv_id = parsing.parse_league_season_bhv_id(league_season_link)

        if self.options['league_seasons'] and bhv_id not in self.options['league_seasons']:
            self.stdout.write('SKIPPING League Season (options): {} {}'.format(bhv_id, abbreviation))
            return

        if abbreviation[:1] in ['m', 'w', 'g', 'u'] and not self.options['youth']:
            self.stdout.write('SKIPPING League Season (youth league): {} {}'.format(bhv_id, abbreviation))
            return

        url = source_url.league_season_source_url(bhv_id)
        dom = logic.get_html(url)

        name = parsing.parse_league_name(dom)

        if logic.is_youth_league(name) and not self.options['youth']:
            self.stdout.write('SKIPPING League Season (youth league): {} {}'.format(bhv_id, name))
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

        league, league_created = models.League.objects.get_or_create(
            name=name, abbreviation=abbreviation, district=district)
        if league_created:
            self.stdout.write('CREATED League: {}'.format(league))
        else:
            self.stdout.write('EXISTING League: {}'.format(league))

        league_season, league_season_created = models.LeagueSeason.objects.get_or_create(
            league=league, season=season, bhv_id=bhv_id)
        if league_season_created:
            self.stdout.write('CREATED League Season: {}'.format(league_season))
        else:
            self.stdout.write('EXISTING League Season: {}'.format(league_season))

        for team_link in team_links:
            self.create_team(team_link, league_season)

    def create_team(self, link, league_season):
        bhv_id = parsing.parse_team_bhv_id(link)
        name = link.text

        url = source_url.team_source_url(league_season.bhv_id, bhv_id)
        dom = logic.get_html(url)
        game_rows = parsing.parse_game_rows(dom)
        short_team_names = [c.text for game_row in game_rows for c in game_row.xpath('td')[4:7:2]]
        short_team_name = max(set(short_team_names), key=short_team_names.count)

        team, created = models.Team.objects.get_or_create(
            name=name, short_name=short_team_name, league_season=league_season, bhv_id=bhv_id)
        if created:
            self.stdout.write('CREATED Team: {}'.format(team))
        else:
            self.stdout.write('EXISTING Team: {}'.format(team))
