import logging

from django.conf import settings
from django.core.management import BaseCommand

from associations.models import Association
from base import http, parsing
from base.middleware import env
from base.models import Value

LOGGER = logging.getLogger("hbscorez")


def add_default_arguments(parser):
    parser.add_argument(
        "--associations",
        "-a",
        nargs="+",
        type=str,
        metavar="short_name",
        help="IDs of Associations.",
    )


class Command(BaseCommand):

    def add_arguments(self, parser):
        add_default_arguments(parser)

    def handle(self, *args, **options):
        env.updating().set_value(Value.TRUE)

        try:
            import_associations(options)
        except Exception:
            LOGGER.exception("Could not import Associations")

        env.updating().set_value(Value.FALSE)


def import_associations(options):
    start_html = http.get_text(settings.HBNET_ROOT_URL + "/verbaende")
    start_dom = parsing.html_dom(start_html)
    association_urls = parsing.parse_association_urls(start_dom)

    for association_url in association_urls:
        try:
            url = settings.HBNET_ROOT_URL + "/" + association_url[1:]
            scrape_association(url, options)
        except Exception:
            LOGGER.exception("Could not create Association")


def scrape_association(url: str, options):
    html = http.get_text(url)
    dom = parsing.html_dom(html)

    name = parsing.parse_association_name(dom)
    short_name = parsing.parse_association_short_name(url)

    if options["associations"] and short_name not in options["associations"]:
        LOGGER.debug("SKIPPING Association (options): %s %s", short_name, name)
        return

    association = Association.objects.filter(short_name=short_name).first()
    if association is None:
        association = Association.objects.create(name=name, short_name=short_name, source_url=url)
        LOGGER.info("CREATED Association: %s", association)
        return

    updated = False

    if association.name != name:
        association.name = name
        updated = True

    if association.source_url != url:
        association.source_url = url
        updated = True

    if updated:
        association.save()
        LOGGER.info("UPDATED Association: %s", association)
    else:
        LOGGER.debug("UNCHANGED Association: %s", association)
