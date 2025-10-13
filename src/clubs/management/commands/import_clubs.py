import logging
from typing import Any

from django.conf import settings
from django.core.management import BaseCommand

from associations.models import Association
from base import http, parsing
from base.middleware import env
from base.models import Value
from districts.models import District
from teams.models import Club, Team

LOGGER = logging.getLogger("hbscorez")


class Command(BaseCommand):
    options: dict[str, Any] = {}

    def add_arguments(self, parser):
        parser.add_argument(
            "--associations", "-a", nargs="+", type=int, metavar="short_name", help="short names of Associations."
        )
        parser.add_argument("--clubs", "-c", nargs="+", type=int, metavar="bhv_id", help="IDs of Clubs.")

    def handle(self, *_, **options):
        self.options = options
        env.updating().set_value(Value.TRUE)
        scrape_associations(options)
        env.updating().set_value(Value.FALSE)


def scrape_associations(options):
    for association in Association.objects.all():
        scrape_association(association, options)


def scrape_association(association: Association, options):
    if options["associations"] and association.short_name not in options["associations"]:
        LOGGER.debug("SKIPPING Association: %s (options)", association)
        return

    LOGGER.info("SCRAPING Association: %s", association)

    url = f"{settings.H4A_ROOT_SPO_URL}/Spielbetrieb/mannschaftsspielplaene.php?orgGrpID={association.short_name}"
    html = http.get_text(url)
    dom = parsing.html_dom(html)

    club_options = parsing.parse_club_option_texts(dom)
    for club_option in club_options:
        (name, bhv_id) = parsing.parse_club_option(club_option)
        import_club(association, name, bhv_id, options)


def import_club(association: Association, name: str, bhv_id, options):
    if options["clubs"] and bhv_id not in options["clubs"]:
        LOGGER.debug("SKIPPING Club (options): %s %s", bhv_id, name)
        return

    if name in [d.name for d in District.objects.all()]:
        LOGGER.debug("SKIPPING Club (District): %s - %s %s", association, bhv_id, name)
        return

    club, created = Club.objects.get_or_create(name=name, bhv_id=bhv_id)
    club.associations.add(association)
    if created:
        LOGGER.info("CREATED Club: %s", club)
    else:
        LOGGER.info("EXISTING Club: %s", club)

    update_teams(club)


def update_teams(club):
    teams = Team.objects.filter(name__regex=rf"^{club.name}( \d)?$")
    for team in teams:
        if team.club is None:
            team.club = club
            team.save()
            LOGGER.info("UPDATED Team (Club): %s - %s ", team, club)
        elif team.club != club:
            LOGGER.warning('CONFLICTING Team Club: %s has "%s" instead of %s"', team, team.club, club)
