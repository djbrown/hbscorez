import logging
from typing import List, Tuple

from django.core.management import BaseCommand
from django.db import transaction

from base import logic
from base.middleware import env
from base.models import Value
from games.models import Game
from players.models import Player, Score

logger = logging.getLogger('hbscorez.command')


class Command(BaseCommand):

    def handle(self, *args, **options):
        env.UPDATING.set_value(Value.TRUE)
        self.rename_player(387733, "Philip Noske", "Philipp Noske")
        self.rename_player(387733, "Frieder Schwarb", "Frieder Schwab")
        self.rename_player(387733, "Patrick Dederich", "Patrick Dederichs")
        sghh = [
            ("David Krypczyk", 1, 0, 0, 0),
            ("Jakob Steinhilper", 4, 0, 0, 0),
            ("Benjamin Boudgoust", 6, 2, 0, 0),
            ("Stephan Keibl", 7, 6, 0, 0),
            ("Yannick Beer", 8, 4, 0, 0),
            ("Jascha Lehnkering", 11, 2, 0, 0),
            ("Daniel Debatin", 12, 0, 0, 0),
            ("Raphael Blum", 13, 0, 0, 0),
            ("Maximilian Strüwing", 19, 3, 4, 3),
            ("Matthias Junker", 14, 3, 2, 1),
            ("Michael Förster", 18, 5, 0, 0),
            ("Maximilian Vollmer", 11, 2, 0, 0),
            ("Daniel Badawi", 17, 1, 0, 0),
        ]
        hcn = [
            ("Julian Frauendorff", 2, 2, 0, 0),
            ("Artur Pietrucha", 5, 7, 0, 0),
            ("Georg Kern", 7, 3, 0, 0),
            ("Jochen Werling", 10, 2, 0, 0),
            ("Findan Krettek", 12, 0, 0, 0),
            ("Paul Nonnenmacher", 17, 0, 0, 0),
            ("Jonas Kraus", 18, 7, 3, 3),
            ("Marius Angrick", 19, 5, 0, 0),
            ("Felix Kracht", 23, 1, 0, 0),
            ("Janick Nölle", 27, 0, 0, 0),
            ("Marco Langjahr", 32, 4, 0, 0),
            ("Kevin Langjahr", 34, 1, 0, 0),
            ("Timo Bäuerlein", 62, 2, 0, 0),
        ]
        self.add_scores(26773, 210116,  sghh, hcn)
        env.UPDATING.set_value(Value.FALSE)

    @transaction.atomic
    def rename_player(self, team_bhv_id, old_name, new_name):
        logger.info("rename Player '{}' ({}) to '{}'".format(old_name, team_bhv_id, new_name))
        try:
            old_player = Player.objects.get(name=old_name, team__bhv_id=team_bhv_id)
            new_player, created = Player.objects.get_or_create(name=new_name, team=old_player.team)
            if old_player == new_player:
                logger.info("skip Player (old equals new): {}".format(new_player))
            else:
                if created:
                    logger.debug("CREATED Player: {}".format(new_player))
                else:
                    logger.debug("EXISTING Player: {}".format(new_player))
                for score in old_player.score_set.all():
                    score.player = new_player
                    score.save()
                old_player.delete()
                logger.info("moved Player: {} to {}".format(old_name, new_player))
        except Player.DoesNotExist:
            logger.warning("skip Player (not found): {} ({})".format(old_name, team_bhv_id))

    @transaction.atomic
    def add_scores(self, league__bhv_id: int, game_number: int,  home_data, guest_data):
        logger.info("add Scores {} {}".format(league__bhv_id, game_number))
        try:
            game = Game.objects.get(league__bhv_id=league__bhv_id, number=game_number)
            if game.score_set.exists():
                logger.warning("skip Game (existing scores): {}".format(game))
            else:
                self._add_scores(game, game.home_team, home_data)
                self._add_scores(game, game.guest_team, guest_data)
        except Game.DoesNotExist:
            logger.warning("skip Game (not found): {} {}".format(league__bhv_id, game_number))

    def _add_scores(self, game, team, data: List[Tuple[str, int, int, int, int]]):
        for score_data in data:
            player = Player(name=score_data[0], team=team)
            score = Score(player=player, player_number=score_data[1], game=game, goals=score_data[2],
                          penalty_tries=score_data[3], penalty_goals=score_data[4])
            logic.add_score(score=score, log_fun=logger.debug)
