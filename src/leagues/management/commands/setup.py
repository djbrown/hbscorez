import logging
from datetime import date, datetime, timedelta

from django.core.management import BaseCommand
from django.db import transaction

from associations.models import Association
from base import http, parsing
from base.middleware import env
from base.models import Value
from districts.models import District
from leagues.models import League, LeagueName, Season
from teams.models import Team

LOGGER = logging.getLogger('hbscorez')


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
        env.UPDATING.set_value(Value.TRUE)

        try:
            setup_associations(options)
        except Exception:
            LOGGER.exception("Could not setup Associations")

        env.UPDATING.set_value(Value.FALSE)


def setup_associations(options):
    associations_filters = {}
    if options['associations']:
        associations_filters['bhv_id__in'] = options['associations']
    associations = Association.objects.filter(**associations_filters)
    associations_bhv_ids = [a.bhv_id for a in associations]

    districts_filters = {'associations__bhv_id__in': associations_bhv_ids}
    if options['districts']:
        districts_filters['bhv_id__in'] = options['districts']
    districts = District.objects.filter(**districts_filters)

    for district in districts:
        try:
            scrape_seasons(district, options)
        except Exception:
            LOGGER.exception("Could not setup Seasons for District %s", district)


def scrape_seasons(district: District, options):
    for start_year in range(2004, datetime.now().year + 1):
        try:
            scrape_season(district, start_year, options)
        except Exception:
            LOGGER.exception("Could not create Season %s for District %s", start_year, district)


def scrape_season(district, start_year, options):
    if options['seasons'] and start_year not in options['seasons']:
        LOGGER.debug('SKIPPING Season (options): %s', start_year)
        return

    season, season_created = Season.objects.get_or_create(start_year=start_year)
    if season_created:
        LOGGER.info('CREATED Season: %s', season)
    else:
        LOGGER.debug('UNCHANGED Season: %s', season)

    for start_date in [date(start_year, 10, 1) + timedelta(days=10 * n) for n in range(4)]:
        LOGGER.debug('trying District Season: %s %s %s', district, season, start_date)
        url = District.build_source_url(district.bhv_id, start_date)
        html = http.get_text(url)
        dom = parsing.html_dom(html)
        league_links = parsing.parse_league_links(dom)
        if league_links:
            break
    else:
        LOGGER.warning('District Season without Leagues: %s %s', district, season)
        return

    for league_link in league_links:
        try:
            scrape_league(league_link, district, season, options)
        except Exception:
            LOGGER.exception("Could not create League %s", league_link)


@transaction.atomic
def scrape_league(league_link, district, season, options):  # pylint: disable=too-many-branches
    abbreviation = league_link.text
    bhv_id = parsing.parse_league_bhv_id(league_link)

    if options['leagues'] and bhv_id not in options['leagues']:
        LOGGER.debug('SKIPPING League (options): %s %s', bhv_id, abbreviation)
        return

    if abbreviation == 'TEST':
        LOGGER.debug('SKIPPING League (test league): %s %s', bhv_id, abbreviation)
        return

    url = League.build_source_url(bhv_id)
    html = http.get_text(url)
    dom = parsing.html_dom(html)
    name = parsing.parse_league_name(dom)

    try:
        name = LeagueName.objects.get(bhv_id=bhv_id).name
    except LeagueName.DoesNotExist:
        pass

    irrelevant_league_name_indicators = [
        'Platzierungsrunde',
        'Kreisvergleichsspiele',
        'pokal', 'Pokal', 'Trophy',
        'Vorbereitung', 'F-FS', 'M-FS', 'Quali',
        'Freiwurf', 'Maxi', 'turnier', 'Turnier', 'Cup', 'wettbewerb',
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

    if League.is_youth(abbreviation, name) and not options['youth']:
        LOGGER.debug('SKIPPING League (youth league): %s %s %s', bhv_id, abbreviation, name)
        return

    league = League.objects.filter(bhv_id=bhv_id).first()
    if league is None:
        league = League.objects.create(name=name, abbreviation=abbreviation,
                                       district=district, season=season, bhv_id=bhv_id)
        LOGGER.info('CREATED League: %s', league)

    updated = False

    if league.name != name:
        league.name = name
        updated = True

    if league.abbreviation != abbreviation:
        league.abbreviation = abbreviation
        updated = True

    if updated:
        league.save()
        LOGGER.info('UPDATED League: %s', league)
    else:
        LOGGER.debug('UNCHANGED League: %s', league)

    if options['skip_teams']:
        return

    for team_link in team_links:
        scrape_team(team_link, league)

    retirements = parsing.parse_retirements(dom)
    Team.check_retirements(retirements, league, LOGGER)


def scrape_team(link, league):
    bhv_id = parsing.parse_team_bhv_id(link)
    name = link.text

    url = Team.build_source_url(league.bhv_id, bhv_id)
    html = http.get_text(url)
    dom = parsing.html_dom(html)
    game_rows = parsing.parse_game_rows(dom)
    short_team_names = parsing.parse_team_short_names(game_rows)
    short_team_name = Team.find_matching_short_name(name, short_team_names)

    Team.create_or_update_team(name, short_team_name, league, bhv_id, LOGGER)
