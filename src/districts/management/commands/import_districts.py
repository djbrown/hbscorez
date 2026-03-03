import logging

from django.core.management import BaseCommand

from associations.models import Association
from base import http, parsing
from base.middleware import env
from base.models import Value
from districts.models import District

LOGGER = logging.getLogger("hbscorez")


class Command(BaseCommand):

    def handle(self, *args, **options):
        env.updating().set_value(Value.TRUE)
        options["processed_districts"] = set()

        try:
            import_districts(options)
        except Exception:
            LOGGER.exception("Could not import Districts")

        env.updating().set_value(Value.FALSE)


def import_districts(options):
    associations_filters = {}
    if options["associations"]:
        associations_filters["short_name__in"] = options["associations"]
    associations = Association.objects.filter(**associations_filters)

    for association in associations:
        try:
            scrape_districs(association, options)
        except Exception:
            LOGGER.exception("Could not scrape Districts for Association %s", associations)


def scrape_districs(association: Association, options):
    url = association.api_url()
    json = http.get_throttled(url)

    districts_names = parsing.parse_districts_names(json)

    for name in districts_names:
        try:
            scrape_district(name, association, options)
        except Exception:
            LOGGER.exception("Could not create District %s", name)


def scrape_district(name, association: Association, options):
    if options["districts"] and name not in options["districts"]:
        LOGGER.debug("SKIPPING District (options): %s", name)
        return

    district = District.objects.filter(name=name).first()
    if district is None:
        district = District.objects.create(name=name)
        LOGGER.info("CREATED District: %s", district)

    if association not in district.associations.all():
        LOGGER.info("ADDING District to Association: %s - %s", association, district)
        district.associations.add(association)

    if name in options["processed_districts"]:
        LOGGER.debug("SKIPPING District: %s (already processed)", district)
        return
    options["processed_districts"].add(name)
