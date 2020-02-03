import logging
from datetime import date, datetime, timedelta

from django.conf import settings
from django.core.management import BaseCommand
from django.db import transaction

from associations.models import Association
from base import logic, parsing
from base.middleware import env
from base.models import Value
from districts.models import District
from leagues.models import League, Season
from teams.models import Team

LOGGER = logging.getLogger('hbscorez')


class Command(BaseCommand):
    options: dict = {}
    processed_districts: set = set()

    def add_arguments(self, parser):
        parser.add_argument('--associations', '-a', nargs='+', type=int, metavar='orgGrpID',
                            help="IDs of Associations.")
        parser.add_argument('--districts', '-d', nargs='+', type=int, metavar='orgID',
                            help="IDs of Districts.")
        parser.add_argument('--seasons', '-s', nargs='+', type=int, metavar='start year',
                            help="Start Years of Seasons.")
        parser.add_argument('--leagues', '-l', nargs='+', type=int, metavar='score/sGID',
                            help="IDs of Leagues.")
        parser.add_argument('--youth', action='store_true',
                            help="Include youth leagues.")
        parser.add_argument('--skip-teams', action='store_true',
                            help="Skip processing Teams.")

    def handle(self, *args, **options):
        self.options = options
        self.processed_districts = set()
        env.UPDATING.set_value(Value.TRUE)
        self.create_associations()
        env.UPDATING.set_value(Value.FALSE)

    def create_associations(self):
        url = settings.NEW_ROOT_SOURCE_URL
        dom = logic.get_html(url)
        portal_paths = dom.xpath('//div[@id="main-content"]//table[@summary]/tbody/tr/td[1]/a/@href')
        for portal_path in portal_paths:
            portal_url = portal_path if portal_path.startswith('http') else settings.NEW_ROOT_SOURCE_URL + portal_path
            bhv_id = self.get_association_bhv_id(portal_url)
            self.create_association(bhv_id)

    def get_association_bhv_id(self, association_portal_url: str) -> int:
        dom = logic.get_html(association_portal_url)
        [bhv_id] = dom.xpath('//div[@id="app"]/@data-og-id')
        return int(bhv_id)

    def create_association(self, bhv_id):
        url = Association.build_source_url(bhv_id)
        dom = logic.get_html(url)

        name = parsing.parse_league_name(dom)
        try:
            abbreviation = Association.get_association_abbreviation(name)
        except KeyError:
            LOGGER.warning("No abbreviation for association '%s'", name)
            return

        if self.options['associations'] and bhv_id not in self.options['associations']:
            LOGGER.debug('SKIPPING Association (options): %s %s', bhv_id, name)
            return

        association, created = Association.objects.get_or_create(name=name, abbreviation=abbreviation, bhv_id=bhv_id)
        if created:
            LOGGER.info('CREATED Association: %s', association)
        else:
            LOGGER.info('EXISTING Association: %s', association)

        items = dom.xpath('//select[@name="orgID"]/option[position()>1]')
        for item in items:
            self.create_district(item, association)

    def create_district(self, district_item, association):
        name = district_item.text
        bhv_id = int(district_item.get('value'))

        if self.options['districts'] and bhv_id not in self.options['districts']:
            LOGGER.debug('SKIPPING District (options): %s %s', bhv_id, name)
            return

        district, created = District.objects.get_or_create(name=name, bhv_id=bhv_id)
        district.associations.add(association)
        if bhv_id in self.processed_districts:
            LOGGER.debug('SKIPPING District: %s %s (already processed)', bhv_id, name)
            return

        if created:
            LOGGER.info('CREATED District: %s', district)
        else:
            LOGGER.info('EXISTING District: %s', district)
        self.processed_districts.add(bhv_id)

        for start_year in range(2004, datetime.now().year + 1):
            self.create_season(district, start_year)

    def create_season(self, district, start_year):
        if self.options['seasons'] and start_year not in self.options['seasons']:
            LOGGER.debug('SKIPPING Season (options): %s', start_year)
            return

        season, season_created = Season.objects.get_or_create(start_year=start_year)
        if season_created:
            LOGGER.info('CREATED Season: %s', season)
        else:
            LOGGER.info('EXISTING Season: %s', season)

        for start_date in [date(start_year, 10, 1) + timedelta(days=10 * n) for n in range(4)]:
            LOGGER.debug('trying District Season: %s %s %s', district, season, start_date)
            url = District.build_source_url(district.bhv_id, start_date)
            dom = logic.get_html(url)
            league_links = dom.xpath('//div[@id="results"]/div/table[2]/tr/td[1]/a')
            if league_links:
                break
        else:
            LOGGER.warning('District Season without Leagues: %s %s', district, season)
            return

        for league_link in league_links:
            self.create_league(league_link, district, season)

    @transaction.atomic
    def create_league(self, league_link, district, season):
        abbreviation = league_link.text
        bhv_id = parsing.parse_league_bhv_id(league_link)

        if self.options['leagues'] and bhv_id not in self.options['leagues']:
            LOGGER.debug('SKIPPING League (options): %s %s', bhv_id, abbreviation)
            return

        if abbreviation == 'TEST':
            LOGGER.debug('SKIPPING League (test league): %s %s', bhv_id, abbreviation)
            return

        url = League.build_source_url(bhv_id)
        dom = logic.get_html(url)
        name = parsing.parse_league_name(dom)

        if any(n in name for n in ['Platzierungsrunde', 'Meister', 'Freiwurf', 'Maxi', 'turnier', 'wettbewerb', 'pokal']):
            LOGGER.debug('SKIPPING League (name): %s %s', bhv_id, name)
            return

        team_links = parsing.parse_team_links(dom)
        if not team_links:
            LOGGER.debug('SKIPPING League (no team table): %s %s', bhv_id, name)
            return

        game_rows = parsing.parse_game_rows(dom)
        if not game_rows:
            LOGGER.debug('SKIPPING League (no games): %s %s', bhv_id, name)
            return

        if len(game_rows) < len(team_links) * (len(team_links) - 1):
            LOGGER.debug('SKIPPING League (few games): %s %s', bhv_id, abbreviation)
            return

        name = {
            5380: "Männer Kreisliga 2-1",
            5381: "Männer Kreisliga 2-2",
            7424: "Männer Kreisliga C Staffel 3",
            50351: "gemischte Jugend D Kreisliga A Staffel 1",
            52853: "männliche Jugend C Bezirksliga Staffel 2",
        }.get(bhv_id, name)

        if League.is_youth(abbreviation, name) and not self.options['youth']:
            LOGGER.debug('SKIPPING League (youth league): %s %s %s', bhv_id, abbreviation, name)
            return

        league, league_created = League.objects.get_or_create(
            name=name, abbreviation=abbreviation, district=district, season=season, bhv_id=bhv_id)
        if league_created:
            LOGGER.info('CREATED League: %s', league)
        else:
            LOGGER.info('EXISTING League: %s', league)

        if self.options['skip_teams']:
            return

        for team_link in team_links:
            create_team(team_link, league)

        retirements = parsing.parse_retirements(dom)
        for team_name, retirement_date in retirements:
            try:
                team = Team.objects.get(league=league, name=team_name)
            except Team.DoesNotExist:
                LOGGER.warning('RETIRING team not found: %s %s', team_name, league)
                continue
            if team.retirement != retirement_date:
                team.retirement = retirement_date
                LOGGER.info('RETIRING team %s on %s', team, retirement_date)
                team.save()


def create_team(link, league):
    bhv_id = parsing.parse_team_bhv_id(link)
    name = link.text

    url = Team.build_source_url(league.bhv_id, bhv_id)
    dom = logic.get_html(url)
    game_rows = parsing.parse_game_rows(dom)
    short_team_names = [c.text for game_row in game_rows for c in game_row.xpath('td')[4:7:2]]
    short_team_name = max(set(short_team_names), key=short_team_names.count)

    team, created = Team.objects.get_or_create(
        name=name, short_name=short_team_name, league=league, bhv_id=bhv_id)
    if created:
        LOGGER.info('CREATED Team: %s', team)
    else:
        LOGGER.info('EXISTING Team: %s', team)
