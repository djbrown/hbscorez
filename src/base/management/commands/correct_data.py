import datetime
import logging
from typing import Any, Dict

from django.core.management import BaseCommand
from django.db import transaction

from base import logic
from base.middleware import env
from base.models import Value
from games.models import Game, Team
from players.models import Player, Score

LOGGER = logging.getLogger('hbscorez.command')


class Command(BaseCommand):

    def handle(self, *args, **options):
        env.UPDATING.set_value(Value.TRUE)
        fix_game_387733()
        fix_game_210116()
        fix_game_96781()
        env.UPDATING.set_value(Value.FALSE)


@transaction.atomic
def rename_player(team_bhv_id, old_name, new_name):
    LOGGER.info("rename Player '%s' (%s) to '%s'", old_name, team_bhv_id, new_name)
    try:
        old_player = Player.objects.get(name=old_name, team__bhv_id=team_bhv_id)
        new_player, created = Player.objects.get_or_create(name=new_name, team=old_player.team)
        if old_player == new_player:
            LOGGER.info('skip Player (old equals new): %s', new_player)
        else:
            if created:
                LOGGER.debug('CREATED Player: %s', new_player)
            else:
                LOGGER.debug('EXISTING Player: %s', new_player)
            for score in old_player.score_set.all():
                score.player = new_player
                score.save()
            old_player.delete()
            LOGGER.info('moved Player: %s to %s', old_name, new_player)
    except Player.DoesNotExist:
        LOGGER.warning('skip Player (not found): %s (%s)', old_name, team_bhv_id)


def _score(player_number: int, goals: int = 0, penalty_tries: int = 0,
           penalty_goals: int = 0, **kwargs) -> Dict[str, Any]:
    return {"player_number": player_number, "goals": goals, "penalty_tries": penalty_tries,
            "penalty_goals": penalty_goals, **kwargs}


def time(minutes: int, seconds: int = 0):
    return datetime.timedelta(minutes=minutes, seconds=seconds)


@transaction.atomic
def add_scores(league__bhv_id: int, game_number: int, home_score_data: Dict[str, Dict[str, Any]],
               guest_score_data: Dict[str, Dict[str, Any]]):
    LOGGER.info('add Scores %s %s', league__bhv_id, game_number)
    try:
        game = Game.objects.get(league__bhv_id=league__bhv_id, number=game_number)
        if game.score_set.exists():
            LOGGER.warning('skip Game (existing scores): %s', game)
        else:
            _add_scores(game, game.home_team, home_score_data)
            _add_scores(game, game.guest_team, guest_score_data)
    except Game.DoesNotExist:
        LOGGER.warning('skip Game (not found): %s %s', league__bhv_id, game_number)


def _add_scores(game: Game, team: Team, scores_data: Dict[str, Dict[str, Any]]):
    for name, score_data in scores_data.items():
        player = Player(name=name, team=team)
        sco = Score(player=player, game=game, **score_data)
        logic.add_score(score=sco)


def fix_game_387733():
    rename_player(387733, "Philip Noske", "Philipp Noske")
    rename_player(387733, "Frieder Schwarb", "Frieder Schwab")
    rename_player(387733, "Patrick Dederich", "Patrick Dederichs")


def fix_game_210116():
    sghh = {
        "David Krypczyk": _score(1),
        "Jakob Steinhilper": _score(4),
        "Benjamin Boudgoust": _score(6, 2),
        "Stephan Keibl": _score(7, 6),
        "Yannick Beer": _score(8, 4),
        "Jascha Lehnkering": _score(11, 2),
        "Daniel Debatin": _score(12),
        "Raphael Blum": _score(13),
        "Maximilian Strüwing": _score(19, 3, 4, 3),
        "Matthias Junker": _score(14, 3, 2, 1),
        "Michael Förster": _score(18, 5),
        "Maximilian Vollmer": _score(11, 2),
        "Daniel Badawi": _score(17, 1),
    }
    hcn = {
        "Julian Frauendorff": _score(2, 2),
        "Artur Pietrucha": _score(5, 7),
        "Georg Kern": _score(7, 3),
        "Jochen Werling": _score(10, 2),
        "Findan Krettek": _score(12),
        "Paul Nonnenmacher": _score(17),
        "Jonas Kraus": _score(18, 7, 3, 3),
        "Marius Angrick": _score(19, 5),
        "Felix Kracht": _score(23, 1),
        "Janick Nölle": _score(27),
        "Marco Langjahr": _score(32, 4),
        "Kevin Langjahr": _score(34, 1),
        "Timo Bäuerlein": _score(62, 2),
    }
    add_scores(26773, 210116, sghh, hcn)


def fix_game_96781():
    tvw = {
        "Johanna Jassinger": _score(3),
        "Katinka Karolyi": _score(4),
        "Nicola Mayer-Rosa": _score(5, 1, warning_time=time(15)),
        "Julia Müller": _score(8),
        "Ann-Kathrin Kübler": _score(10, 1),
        "Amela Celahmetovic": _score(11),
        "Stephanie Schneider": _score(13, 5, warning_time=time(11)),
        "Lea Frankenhauser": _score(14, 6),
        "Nicole Monika Spänle": _score(16),
        "Nadja Meier": _score(17, 1),
        "Barbara Koch": _score(18, 4, 1, 1),
        "Matilda Obermeier": _score(24),
        "Jeannette Pfahl": _score(25),
        "Miriam Borrmann": _score(76, 1, 1, 1),
    }
    sga = {
        "Wiebke Krause": _score(1),
        "Lydia Hepp": _score(2, 1, first_suspension_time=time(50, 21)),
        "Dalin Kozok": _score(5, 2, warning_time=time(9), first_suspension_time=time(21, 36)),
        "Katharina Stellmacher": _score(6, first_suspension_time=time(27, 16)),
        "Jessica Mayer": _score(7, 1),
        "Selina Haack": _score(8, 2, warning_time=time(6)),
        "Janina Hirscher": _score(9, 8),
        "Leonie Wölfle": _score(13, 1),
        "Ramona Endraß": _score(14, 7, warning_time=time(14), first_suspension_time=time(40, 37)),
        "Lisa Dreher": _score(17),
        "Cathrin Müller": _score(16),
        "Annika Duttle": _score(15, 1),
        "Ann-Kathrin Messner": _score(19),
    }
    add_scores(league__bhv_id=45956, game_number=96781, home_score_data=tvw, guest_score_data=sga)
