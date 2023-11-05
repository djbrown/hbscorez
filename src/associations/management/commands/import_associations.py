import logging

from django.conf import settings
from django.core.management import BaseCommand

from associations.models import Association
from base import http, parsing
from base.middleware import env
from base.models import Value

LOGGER = logging.getLogger('hbscorez')


def add_default_arguments(parser):
    parser.add_argument('--associations', '-a', nargs='+', type=int, metavar='orgGrpID',
                        help="IDs of Associations.")


class Command(BaseCommand):

    def add_arguments(self, parser):
        add_default_arguments(parser)

    def handle(self, *args, **options):
        env.UPDATING.set_value(Value.TRUE)

        try:
            import_associations(options)
        except Exception:
            LOGGER.exception("Could not import Associations")

        env.UPDATING.set_value(Value.FALSE)


def import_associations(options):
    start_html = http.get_text(settings.NEW_ROOT_SOURCE_URL)
    start_dom = parsing.html_dom(start_html)
    association_urls = parsing.parse_association_urls(start_dom)

    for association_url in association_urls:
        try:
            scrape_association(association_url, options)
        except Exception:
            LOGGER.exception("Could not create Association")


def scrape_association(url: str, options):
    html = http.get_text(url)
    dom = parsing.html_dom(html)

    bhv_id = parsing.parse_association_bhv_id(dom)
    name = parsing.parse_association_name(dom)
    
    association_api_url = f'{settings.API_URL_TEMPLATE}cmd=po&og={bhv_id}'
    abbreviation = parsing.parse_association_abbreviation(association_api_url)

    if options['associations'] and bhv_id not in options['associations']:
        LOGGER.debug('SKIPPING Association (options): %s %s', bhv_id, name)
        return

    try:
        association = Association.objects.get(bhv_id=bhv_id)
    except Association.MultipleObjectsReturned:
        LOGGER.debug('Database contains multiple association objects with same bhv_id.')
        return
    except Association.DoesNotExist:
        association = Association.objects.create(name=name, abbreviation=abbreviation, bhv_id=bhv_id)
        LOGGER.info('CREATED Association: %s', association)
        return

    updated = False

    if association.name != name:
        association.name = name
        updated = True

    if updated:
        association.save()
        LOGGER.info('UPDATED Association: %s', association)
    else:
        LOGGER.debug('UNCHANGED Association: %s', association)
