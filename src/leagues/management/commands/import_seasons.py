import logging

from django.core.management import BaseCommand

from associations.models import Association
from base import http, parsing
from base.middleware import env
from base.models import Value
from leagues.models import Season

LOGGER = logging.getLogger("hbscorez")


def add_default_arguments(parser):
    parser.add_argument("--seasons", "-s", nargs="+", type=int, metavar="start year", help="Start Years of Seasons.")


class Command(BaseCommand):

    def add_arguments(self, parser):
        add_default_arguments(parser)

    def handle(self, *args, **options):
        env.updating().set_value(Value.TRUE)

        try:
            import_seasons(options)
        except Exception:
            LOGGER.exception("Could not import Seasons")

        env.updating().set_value(Value.FALSE)


def import_seasons(options):
    try:
        scrape_seasons(options)
    except Exception:
        LOGGER.exception("Could not scrape Seasons")


def scrape_seasons(options):
    url = Association.build_api_url(bhv_id=76)
    json = http.get_throttled(url)

    season_items = parsing.parse_association_season_items(json)

    for bhv_id, name in season_items.items():
        if name.startswith("S "):
            LOGGER.debug("SKIPPING Season (Summer): %s", name)
            continue

        start_year = parsing.parse_season_start_year(name)

        if options["seasons"] and start_year not in options["seasons"]:
            LOGGER.debug("SKIPPING Season (options): %s", start_year)
            continue

        season, season_created = Season.objects.get_or_create(start_year=start_year, bhv_id=int(bhv_id))
        if season_created:
            LOGGER.info("CREATED Season: %s", season)
        else:
            LOGGER.debug("UNCHANGED Season: %s", season)
