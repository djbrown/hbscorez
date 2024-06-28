import logging

from django.core.management import BaseCommand

from associations.management.commands.import_associations import add_default_arguments as association_arguments
from associations.models import Association
from base import http, parsing
from base.middleware import env
from base.models import Value
from districts.models import District

LOGGER = logging.getLogger("hbscorez")


def add_default_arguments(parser):
    association_arguments(parser)
    parser.add_argument("--districts", "-d", nargs="+", type=int, metavar="orgID", help="IDs of Districts.")


class Command(BaseCommand):

    def add_arguments(self, parser):
        add_default_arguments(parser)

    def handle(self, *args, **options):
        env.UPDATING.set_value(Value.TRUE)
        options["processed_districts"] = set()

        try:
            import_districts(options)
        except Exception:
            LOGGER.exception("Could not import Districts")

        env.UPDATING.set_value(Value.FALSE)


def import_districts(options):
    associations_filters = {}
    if options["associations"]:
        associations_filters["bhv_id__in"] = options["associations"]
    associations = Association.objects.filter(**associations_filters)

    for association in associations:
        try:
            scrape_districs(association, options)
        except Exception:
            LOGGER.exception("Could not scrape Districts for Association %s", associations)


def scrape_districs(association: Association, options):
    url = association.api_url()
    json = http.get_text(url)

    districts = parsing.parse_district_items(json)

    for bhv_id, name in districts.items():
        try:
            scrape_district(int(bhv_id), name, association, options)
        except Exception:
            LOGGER.exception("Could not create District %s %s", bhv_id, name)


def scrape_district(bhv_id, name, association: Association, options):
    if options["districts"] and bhv_id not in options["districts"]:
        LOGGER.debug("SKIPPING District (options): %s %s", bhv_id, name)
        return

    district = District.objects.filter(bhv_id=bhv_id).first()
    if district is None:
        district = District.objects.create(name=name, bhv_id=bhv_id)
        LOGGER.info("CREATED District: %s", district)

    if association not in district.associations.all():
        LOGGER.info("ADDING District to Association: %s - %s", association, district)
        district.associations.add(association)

    if bhv_id in options["processed_districts"]:
        LOGGER.debug("SKIPPING District: %s (already processed)", district)
        return
    options["processed_districts"].add(bhv_id)

    updated = False

    if district.name != name:
        district.name = name
        updated = True

    if updated:
        district.save()
        LOGGER.info("UPDATED District: %s", district)
    else:
        LOGGER.debug("UNCHANGED District: %s", district)
