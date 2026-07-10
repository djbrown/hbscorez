import logging
from datetime import date, datetime, timedelta

from django.core.management import BaseCommand
from django.db import transaction

from associations.models import Association
from base import http, parsing
from base.middleware import env
from base.models import Value
from clubs.models import Club
from districts.management.commands.import_districts import add_default_arguments as district_arguments
from districts.models import District
from leagues.models import League, LeagueName, Season
from teams.models import Team

LOGGER = logging.getLogger("hbscorez")


def add_default_arguments(parser):
    district_arguments(parser)
    parser.add_argument("--seasons", "-s", nargs="+", type=int, metavar="start year", help="Start Years of Seasons.")
    parser.add_argument("--leagues", "-l", nargs="+", type=int, metavar="score/sGID", help="IDs of Leagues.")
    parser.add_argument("--youth", action="store_true", help="Include youth leagues.")


class Command(BaseCommand):

    def add_arguments(self, parser):
        add_default_arguments(parser)
        parser.add_argument("--skip-teams", action="store_true", help="Skip processing Teams.")

    def handle(self, *args, **options):
        env.updating().set_value(Value.TRUE)

        try:
            import_leagues(options)
        except Exception:
            LOGGER.exception("Could not import Leagues")

        env.updating().set_value(Value.FALSE)


def import_leagues(options):
    associations_filters = {}
    if options["associations"]:
        associations_filters["bhv_id__in"] = options["associations"]
    associations = Association.objects.filter(**associations_filters)
    associations_bhv_ids = [a.bhv_id for a in associations]
    if not associations:
        LOGGER.warning("No matching Associations found.")
        return

    districts_filters = {"associations__bhv_id__in": associations_bhv_ids}
    if options["districts"]:
        districts_filters["bhv_id__in"] = options["districts"]
    districts = District.objects.filter(**districts_filters)
    if not districts:
        LOGGER.warning("No matching Districts found.")
        return

    seasons = create_seasons(options)

    for district in districts:
        for season in seasons:
            try:
                scrape_district_season(district, season, options)
            except Exception:
                LOGGER.exception("Could not create Leagues for District %s in Season %s", district, season)


def create_seasons(options):
    seasons = []

    for start_year in range(2004, datetime.now().year + 1):
        if options["seasons"] and start_year not in options["seasons"]:
            LOGGER.debug("SKIPPING Season (options): %s", start_year)
            continue

        season, season_created = Season.objects.get_or_create(start_year=start_year)
        seasons.append(season)
        if season_created:
            LOGGER.info("CREATED Season: %s", season)
        else:
            LOGGER.debug("UNCHANGED Season: %s", season)

    return seasons


def scrape_district_season(district: District, season: Season, options):
    season_begin = date(season.start_year, 10, 1)
    interval_days = 10
    interval_count = 4
    for interval_number in range(interval_count):
        interval_date = season_begin + timedelta(days=interval_days * interval_number)
        LOGGER.debug("trying District Season: %s %s %s", district, season, interval_date)
        url = district.api_url(date=interval_date)
        json = http.get_throttled(url)
        league_bhv_ids = parsing.parse_league_bhv_ids(json)
        if league_bhv_ids:
            break
    else:
        LOGGER.warning("District Season without Leagues: %s %s", district, season)
        return

    for league_bhv_id in league_bhv_ids:
        try:
            scrape_league(league_bhv_id, district, season, options)
        except Exception:
            LOGGER.exception("Could not create League %s", league_bhv_id)


@transaction.atomic
def scrape_league(bhv_id, district, season, options):  # pylint: disable=too-many-branches
    if options["leagues"] and bhv_id not in options["leagues"]:
        LOGGER.debug("SKIPPING League (options): %s", bhv_id)
        return

    url = League.build_api_url(district.bhv_id, bhv_id)
    json = http.get_throttled(url)
    name = parsing.parse_league_name(json)
    abbreviation = parsing.parse_league_abbreviation(json)

    if abbreviation == "TEST":
        LOGGER.debug("SKIPPING League (test league): %s %s", bhv_id, abbreviation)
        return

    try:
        name = LeagueName.objects.get(bhv_id=bhv_id).name
    except LeagueName.DoesNotExist:
        pass

    irrelevant_league_name_indicators = [
        "Platzierungsrunde",
        "Kreisvergleichsspiele",
        "pokal",
        "Pokal",
        "Trophy",
        "Vorbereitung",
        "F-FS",
        "M-FS",
        "Quali",
        "Freiwurf",
        "Maxi",
        "turnier",
        "Turnier",
        "Cup",
        "wettbewerb",
        "Test",
        "Planung",
        "planung",
    ]

    if any(n in name for n in irrelevant_league_name_indicators):
        LOGGER.debug("SKIPPING League (name): %s %s", bhv_id, name)
        return

    team_bhv_ids = parsing.parse_team_bhv_ids(json)
    if not team_bhv_ids:
        LOGGER.debug("SKIPPING League (no teams): %s %s", bhv_id, name)
        return

    games = parsing.parse_game_items(json)
    if not games:
        LOGGER.debug("SKIPPING League (no games): %s %s", bhv_id, name)
        return

    if League.is_youth(abbreviation, name) and not options["youth"]:
        LOGGER.debug("SKIPPING League (youth league): %s %s %s", bhv_id, abbreviation, name)
        return

    league = League.objects.filter(bhv_id=bhv_id).first()
    if league is None:
        league = League.objects.create(
            name=name, abbreviation=abbreviation, district=district, season=season, bhv_id=bhv_id
        )
        LOGGER.info("CREATED League: %s", league)

    updated = False

    if league.name != name:
        league.name = name
        updated = True

    if league.abbreviation != abbreviation:
        league.abbreviation = abbreviation
        updated = True

    if updated:
        league.save()
        LOGGER.info("UPDATED League: %s", league)
    else:
        LOGGER.debug("UNCHANGED League: %s", league)

    if options["skip_teams"]:
        return

    for team_bhv_id in team_bhv_ids:
        scrape_team(team_bhv_id, league)

    retirements = parsing.parse_retirements(json)
    Team.check_retirements(retirements, league, LOGGER)


def scrape_team(link, league):
    bhv_id = parsing.parse_team_bhv_id(link)
    name = link.text

    club_name = parsing.parse_team_club_name(name)
    club = Club.objects.filter(name=club_name).first()

    url = Team.build_source_url(league.bhv_id, bhv_id)
    html = http.get_text(url)
    dom = parsing.html_dom(html)
    game_rows = parsing.parse_game_rows(dom)
    short_team_names = parsing.parse_team_short_names(game_rows)
    short_team_name = Team.find_matching_short_name(name, short_team_names)

    Team.create_or_update_team(
        name=name, short_name=short_team_name, league=league, club=club, bhv_id=bhv_id, logger=LOGGER
    )
