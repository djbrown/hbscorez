import logging

from django.core.management import BaseCommand

from associations.management.commands.import_associations import add_association_arguments
from associations.models import Association
from base import http, parsing
from base.middleware import env
from base.models import Value

# from clubs.models import Club
from districts.management.commands.import_districts import add_district_arguments
from districts.models import District
from leagues.management.commands.import_leagues import add_league_arguments
from leagues.management.commands.import_seasons import add_season_arguments
from leagues.models import League, Season

# from teams.models import Team

LOGGER = logging.getLogger("hbscorez")


def add_team_arguments(parser):
    parser.add_argument("--teams", "-t", nargs="+", type=int, metavar="team id", help="IDs of Teams.")


class Command(BaseCommand):

    def add_arguments(self, parser):
        add_association_arguments(parser)
        add_district_arguments(parser)
        add_season_arguments(parser)
        add_league_arguments(parser)
        add_team_arguments(parser)

    def handle(self, *args, **options):
        env.updating().set_value(Value.TRUE)

        try:
            import_teams(options)
        except Exception:
            LOGGER.exception("Could not import Teams")

        env.updating().set_value(Value.FALSE)


def import_teams(options):
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
    districts_bhv_ids = [d.bhv_id for d in districts]
    if not districts:
        LOGGER.warning("No matching Districts found.")
        return

    seasons_filters = {}
    if options["seasons"]:
        seasons_filters["start_year__in"] = options["seasons"]
    seasons = Season.objects.filter(**seasons_filters)
    seasons_start_years = [s.start_year for s in seasons]
    if not seasons:
        LOGGER.warning("No matching Season found.")
        return

    league_filters = {
        "districts__associations__bhv_id__in": associations_bhv_ids,
        "districts__bhv_id__in": districts_bhv_ids,
        "season__start_year__in": seasons_start_years,
    }
    if options["leagues"]:
        league_filters["bhv_id__in"] = options["leagues"]
    leagues = League.objects.filter(**league_filters)
    if not seasons:
        LOGGER.warning("No matching Season found.")
        return

    for league in leagues:
        try:
            scrape_teams(league, options)
        except Exception:
            LOGGER.exception("Could not create Teams for League %s", league)


def scrape_teams(league: League, options):
    url = league.api_url()
    json = http.get_throttled(url)
    team_bhv_ids = parsing.parse_team_bhv_ids(json)
    if not team_bhv_ids:
        LOGGER.debug("SKIPPING League (no Teams): %s", league)
        return

    for team_bhv_id in team_bhv_ids:
        try:
            scrape_team(team_bhv_id, league, options)
        except Exception:
            LOGGER.exception("Could not create League %s", team_bhv_id)


def scrape_team(bhv_id, league, options):
    if options["teams"] and bhv_id not in options["teams"]:
        LOGGER.debug("SKIPPING Team (options): %s", bhv_id)
        return

    # club_name = parsing.parse_team_club_name(name)
    # club = Club.objects.filter(name=club_name).first()

    # url = Team.build_source_url(league.bhv_id, bhv_id)
    # json = http.get_text(url)
    # dom = parsing.html_dom(html)
    # game_rows = parsing.parse_game_rows(dom)
    # short_team_names = parsing.parse_team_short_names(game_rows)
    # short_team_name = Team.find_matching_short_name(name, short_team_names)

    # Team.create_or_update_team(
    #     name=name, short_name=short_team_name, league=league, club=club, bhv_id=bhv_id, logger=LOGGER
    # )
