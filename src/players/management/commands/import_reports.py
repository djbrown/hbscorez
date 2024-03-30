import logging
from pathlib import Path
from typing import Any

import tabula
from django.conf import settings
from django.core.management import BaseCommand
from django.db import transaction

from associations.models import Association
from base import http
from base.middleware import env
from base.models import Value
from games.models import Game
from leagues.management.commands.import_leagues import add_default_arguments
from leagues.models import Season
from players.management.commands import parse_report
from players.models import ReportsBlacklist

LOGGER = logging.getLogger("hbscorez")


class Command(BaseCommand):
    options: dict[str, Any] = {}

    def add_arguments(self, parser):
        add_default_arguments(parser)
        parser.add_argument(
            "--games",
            "-g",
            nargs="+",
            type=int,
            metavar="game number",
            help="numbers of Games.",
        )
        parser.add_argument(
            "--skip-games",
            "-G",
            nargs="+",
            type=int,
            metavar="game number",
            help="numbers of Games.",
        )
        parser.add_argument(
            "--force-update",
            "-f",
            action="store_true",
            help="force download and overwrite if report already exists",
        )

    def handle(self, *args, **options):
        self.options = options
        settings.REPORTS_PATH.mkdir(parents=True, exist_ok=True)
        env.UPDATING.set_value(Value.TRUE)
        self.import_associations()
        env.UPDATING.set_value(Value.FALSE)

    def import_associations(self):
        for association in Association.objects.all():
            self.import_association(association)

    def import_association(self, association):
        if self.options["associations"] and association.bhv_id not in self.options["associations"]:
            LOGGER.debug("SKIPPING Association: %s (options)", association)
            return

        for district in association.district_set.all():
            self.import_district(district)

    def import_district(self, district):
        if self.options["districts"] and district.bhv_id not in self.options["districts"]:
            LOGGER.debug("SKIPPING District: %s (options)", district)
            return

        season_pks = district.league_set.values("season").distinct()
        seasons = Season.objects.filter(pk__in=season_pks)
        for season in seasons:
            self.import_district_season(district, season)

    def import_district_season(self, district, season):
        if self.options["seasons"] and season.start_year not in self.options["seasons"]:
            LOGGER.debug("SKIPPING District Season: %s %s (options)", district, season)
            return

        for league in district.league_set.filter(season=season):
            self.import_league(league)

    def import_league(self, league):
        if self.options["leagues"] and league.bhv_id not in self.options["leagues"]:
            LOGGER.debug("SKIPPING League: %s (options)", league)
            return

        if league.youth and not self.options["youth"]:
            LOGGER.debug("SKIPPING League (youth league): %s", league)
            return

        for game in league.game_set.all():
            try:
                self.import_game(game)
            except Exception:
                LOGGER.exception("Could not import Report")

    def import_game(self, game: Game):
        if self.options["games"] and game.number not in self.options["games"]:
            LOGGER.debug("SKIPPING Game (options): %s - %s", game.report_number, game)
            return

        if game.report_number is None:
            LOGGER.debug("SKIPPING Game (no report): %s - %s", game.report_number, game)
            return

        if ReportsBlacklist.objects.filter(report_number=game.report_number):
            LOGGER.debug("SKIPPING Report (blacklist): %s - %s", game.report_number, game)
            return

        if game.home_team.retirement is not None or game.guest_team.retirement is not None:
            if game.score_set.count() > 0:
                game.score_set.all().delete()
                LOGGER.info("DELETED Game Scores (retired team): %s - %s", game.report_number, game)
            else:
                LOGGER.debug("SKIPPING Game (retired team): %s - %s", game.report_number, game)
            return

        if game.score_set.count() > 0:
            if not self.options["force_update"]:
                LOGGER.debug("SKIPPING Game (existing scores): %s - %s", game.report_number, game)
            else:
                LOGGER.info("REIMPORTING Report: %s - %s", game.report_number, game)
                game.score_set.all().delete()
                import_game(game)
            return

        if game.forfeiting_team is not None:
            LOGGER.debug("SKIPPING Game (forfeit): %s - %s", game.report_number, game)
            return

        LOGGER.info("IMPORTING Report: %s - %s", game.report_number, game)
        import_game(game)


@transaction.atomic
def import_game(game: Game):
    report_file: Path = settings.REPORTS_PATH / str(game.report_number)
    report_file.with_suffix(".pdf")
    download_report(game, report_file)
    import_report(game, report_file)
    report_file.unlink()


def download_report(game: Game, path: Path):
    url = game.report_source_url()
    try:
        content: bytes = http.get_file(url)
    except http.EmptyResponseError:
        LOGGER.warning("SKIPPING Report (empty file): %s - %s", game.report_number, game)
        return

    path.write_bytes(content)


def import_report(game: Game, path: Path):
    [spectators_table, _, home_table, guest_table] = tabula.read_pdf(
        path.absolute(), output_format="json", pages=[1, 2], lattice=True
    )

    game.spectators = parse_report.parse_spectators(spectators_table)
    game.save()

    parse_report.import_scores(home_table, game=game, team=game.home_team)
    parse_report.import_scores(guest_table, game=game, team=game.guest_team)
