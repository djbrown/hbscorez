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
from leagues.models import League, LeagueName, Season
from teams.models import Team

LOGGER = logging.getLogger('hbscorez')

BUGGED_LEAGUES = [80136, 68361]


def add_default_arguments(parser):
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


class Command(BaseCommand):

    def add_arguments(self, parser):
        add_default_arguments(parser)
        parser.add_argument('--skip-teams', action='store_true',
                            help="Skip processing Teams.")

    def handle(self, *args, **options):
        options['processed_districts'] = set()
        env.UPDATING.set_value(Value.TRUE)
        create_associations(options)
        env.UPDATING.set_value(Value.FALSE)


def create_associations(options):
    url = settings.NEW_ROOT_SOURCE_URL
    dom = logic.get_html(url)
    portal_paths = dom.xpath('//div[@id="main-content"]//table[@summary]/tbody/tr/td[1]/a/@href')
    for portal_path in portal_paths:
        portal_url = portal_path if portal_path.startswith('http') else settings.NEW_ROOT_SOURCE_URL + portal_path
        bhv_id = get_association_bhv_id(portal_url)
        try:
            create_association(bhv_id, options)
        except Exception:
            logging.getLogger('mail').exception("Could not create Association")


def get_association_bhv_id(association_portal_url: str) -> int:
    dom = logic.get_html(association_portal_url)
    [bhv_id] = dom.xpath('//div[@id="app"]/@data-og-id')
    return int(bhv_id)


def create_association(bhv_id, options):
    url = Association.build_source_url(bhv_id)
    dom = logic.get_html(url)

    name = parsing.parse_association_name(dom)
    try:
        abbreviation = Association.get_association_abbreviation(name)
    except KeyError:
        LOGGER.warning("No abbreviation for association '%s'", name)
        return

    if options['associations'] and bhv_id not in options['associations']:
        LOGGER.debug('SKIPPING Association (options): %s %s', bhv_id, name)
        return

    association, created = Association.objects.get_or_create(name=name, abbreviation=abbreviation, bhv_id=bhv_id)
    if created:
        LOGGER.info('CREATED Association: %s', association)
    else:
        LOGGER.info('EXISTING Association: %s', association)

    items = dom.xpath('//select[@name="orgID"]/option[position()>1]')
    for item in items:
        try:
            create_district(item, association, options)
        except Exception:
            logging.getLogger('mail').exception("Could not create District")


def create_district(district_item, association: Association, options):
    name = district_item.text
    bhv_id = int(district_item.get('value'))

    if options['districts'] and bhv_id not in options['districts']:
        LOGGER.debug('SKIPPING District (options): %s %s', bhv_id, name)
        return

    district, created = District.objects.get_or_create(name=name, bhv_id=bhv_id)
    district.associations.add(association)
    if bhv_id in options['processed_districts']:
        LOGGER.debug('SKIPPING District: %s %s (already processed)', bhv_id, name)
        return

    if created:
        LOGGER.info('CREATED District: %s', district)
    else:
        LOGGER.info('EXISTING District: %s', district)
    options['processed_districts'].add(bhv_id)

    for start_year in range(2004, datetime.now().year + 1):
        try:
            create_season(district, start_year, options)
        except Exception:
            logging.getLogger('mail').exception("Could not create Season")


def create_season(district, start_year, options):
    if options['seasons'] and start_year not in options['seasons']:
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
        try:
            create_league(league_link, district, season, options)
        except Exception:
            logging.getLogger('mail').exception("Could not create League")


@transaction.atomic
def create_league(league_link, district, season, options):
    abbreviation = league_link.text
    bhv_id = parsing.parse_league_bhv_id(league_link)

    if bhv_id in BUGGED_LEAGUES:
        LOGGER.debug('SKIPPING League (ignore list): %s %s', bhv_id, abbreviation)
        return

    if options['leagues'] and bhv_id not in options['leagues']:
        LOGGER.debug('SKIPPING League (options): %s %s', bhv_id, abbreviation)
        return

    if abbreviation == 'TEST':
        LOGGER.debug('SKIPPING League (test league): %s %s', bhv_id, abbreviation)
        return

    url = League.build_source_url(bhv_id)
    dom = logic.get_html(url)
    name = parsing.parse_league_name(dom)

    irrelevant_league_name_indicators = [
        'Platzierungsrunde',
        'Kreisvergleichsspiele',
        'pokal', 'Pokal', 'Trophy',
        'Vorbereitung', 'F-FS', 'M-FS', 'Quali',
        'Freiwurf', 'Maxi', 'turnier', 'wettbewerb',
        'Test', 'Planung', 'planung',
    ]

    if any(n in name for n in irrelevant_league_name_indicators):
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

    try:
        name = LeagueName.objects.get(bhv_id=bhv_id).name
    except LeagueName.DoesNotExist:
        pass

    if League.is_youth(abbreviation, name) and not options['youth']:
        LOGGER.debug('SKIPPING League (youth league): %s %s %s', bhv_id, abbreviation, name)
        return

    league, league_created = League.objects.get_or_create(
        name=name, abbreviation=abbreviation, district=district, season=season, bhv_id=bhv_id)
    if league_created:
        LOGGER.info('CREATED League: %s', league)
    else:
        LOGGER.info('EXISTING League: %s', league)

    if options['skip_teams']:
        return

    for team_link in team_links:
        create_team(team_link, league)

    retirements = parsing.parse_retirements(dom)
    check_retirements(retirements, league)


def create_team(link, league):
    bhv_id = parsing.parse_team_bhv_id(link)
    name = link.text

    url = Team.build_source_url(league.bhv_id, bhv_id)
    dom = logic.get_html(url)
    game_rows = parsing.parse_game_rows(dom)
    short_team_names = [c.text for game_row in game_rows for c in game_row.xpath('td')[4:7:2]]
    short_team_name = Team.find_matching_short_name(name, short_team_names)

    Team.create_or_update_team(name, short_team_name, league, bhv_id, LOGGER)


def check_retirements(retirements, league):
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
