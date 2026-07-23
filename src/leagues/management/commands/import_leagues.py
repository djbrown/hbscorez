import logging

from django.core.management import BaseCommand
from django.db import transaction

from associations.management.commands.import_associations import add_association_arguments
from associations.models import Association
from base import http, parsing
from base.middleware import env
from base.models import Value
from districts.management.commands.import_districts import add_district_arguments
from districts.models import District
from leagues.management.commands.import_seasons import add_season_arguments
from leagues.models import League, LeagueName, Season

LOGGER = logging.getLogger("hbscorez")


def add_league_arguments(parser):
    parser.add_argument("--leagues", "-l", nargs="+", type=int, metavar="cl/lId", help="IDs of Leagues.")
    parser.add_argument("--youth", action="store_true", help="Include youth leagues.")


class Command(BaseCommand):

    def add_arguments(self, parser):
        add_association_arguments(parser)
        add_district_arguments(parser)
        add_season_arguments(parser)
        add_league_arguments(parser)

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

    seasons_filters = {}
    if options["seasons"]:
        seasons_filters["start_year__in"] = options["seasons"]
    seasons = Season.objects.filter(**seasons_filters)
    if not seasons:
        LOGGER.warning("No matching Season found.")
        return

    for district in districts:
        for season in seasons:
            try:
                scrape_leagues(district, season, options)
            except Exception:
                LOGGER.exception("Could not scrape Leagues for District %s in Season %s", district, season)


def scrape_leagues(district: District, season: Season, options):
    url = district.api_url(season_bhv_id=season.bhv_id)
    json = http.get_throttled(url)
    leagues_bhv_ids = parsing.parse_league_bhv_ids(json)
    if not leagues_bhv_ids:
        LOGGER.warning("District Season without Leagues: %s %s", district, season)
        return

    for league_bhv_id in leagues_bhv_ids:
        try:
            scrape_league(league_bhv_id, district, season, options)
        except Exception:
            LOGGER.exception("Could not scrape League %s", league_bhv_id)


@transaction.atomic
def scrape_league(bhv_id, district, season, options):  # pylint: disable=too-many-branches
    if options["leagues"] and bhv_id not in options["leagues"]:
        LOGGER.debug("SKIPPING League (options): %s", bhv_id)
        return

    url = League.build_api_url(district.bhv_id, bhv_id)
    json = http.get_throttled(url, wait=5)
    if "permission denied" in json:
        LOGGER.warning("SKIPPING League (unauthorized): %s - Season: %s - District %s", bhv_id, season, district)
        return

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

    teams = parsing.parse_team_items(json)
    if not teams:
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

    if league.district != district:
        league.district = district
        updated = True

    if league.season != season:
        league.season = season
        updated = True

    if updated:
        league.save()
        LOGGER.info("UPDATED League: %s", league)
    else:
        LOGGER.debug("UNCHANGED League: %s", league)
