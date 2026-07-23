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
from teams.models import Team

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
    if not leagues:
        LOGGER.warning("No matching League found.")
        return

    for league in leagues:
        try:
            scrape_teams(league, options)
        except Exception:
            LOGGER.exception("Could not scrape Teams for League %s", league)


def scrape_teams(league: League, options):
    url = league.api_url()
    json = http.get_throttled(url)
    team_items = parsing.parse_team_items(json)
    if not team_items:
        LOGGER.debug("SKIPPING League (no Teams): %s", league)
        return

    for team_bhv_id, team_name in team_items.items():
        try:
            create_team(team_bhv_id, team_name, league, options)
        except Exception:
            LOGGER.exception("Could not create Team %s in League %s", team_bhv_id, league)


def create_team(bhv_id, name, league, options):
    if options["teams"] and bhv_id not in options["teams"]:
        LOGGER.debug("SKIPPING Team (options): %s %s", bhv_id, name)
        return

    # club_name = parsing.parse_team_club_name(name)
    # club = Club.objects.filter(name=club_name).first()

    team = Team.objects.filter(bhv_id=bhv_id).first()
    if team is None:
        team = Team.objects.create(name=name, short_name=name, league=league, club=None, bhv_id=bhv_id)
        LOGGER.info("CREATED Team: %s", team)
        return

    updated = False

    if team.name != name:
        team.name = name
        updated = True

    if team.short_name != name:
        team.short_name = name
        updated = True

    if team.league != league:
        team.league = league
        updated = True

    # if team.club != club:
    #     team.club = club
    #     updated = True

    if updated:
        team.save()
        LOGGER.info("UPDATED Team: %s", team)
    else:
        LOGGER.debug("UNCHANGED Team: %s", team)
