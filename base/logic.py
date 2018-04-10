import re
# import time
from typing import Callable

import requests
from django.db import transaction
from lxml import html

from base import models


def get_html(url):
    # time.sleep(1)
    response = requests.get(url)
    response.encoding = 'utf-8'
    return html.fromstring(response.text)


def get_association_abbreviation(association_name):
    association_abbreviations = {
        'Badischer Handball-Verband': 'BHV',
        'Fédération Luxembourgeoise de Handball': 'FLH',
        'Hamburger Handball-Verband': 'HHV',
        'Handball Baden-Württemberg': 'HBW',
        'Handballoberliga Rheinland-Pfalz/Saar': 'RPS',
        'Handballverband Rheinhessen': 'HVR',
        'Handballverband Saar': 'HVS',
        'Handballverband Schleswig-Holstein': 'HVSH',
        'Handballverband Württemberg': 'HVW',
        'Mitteldeutscher Handball-Verband': 'MHV',
        'Oberliga Hamburg - Schleswig-Holstein': 'HHSH',
        'Südbadischer Handballverband': 'SHV',
        'Thüringer Handball-Verband': 'THV',
        'Vorarlberger Handballverband': 'VHV',
    }
    return association_abbreviations[association_name]


def is_youth_league(name):
    return re.search('MJ', name) \
           or re.search('WJ', name) \
           or re.search('Jugend', name) \
           or re.search('Mini', name)


def add_ranking_place(items: list, field: str):
    """
    Adds 'place' to all items according to their order.
    If the value of the specified field on any given item matches the value on the field of the previous item,
    then the item gets the same place as its predecessor.

    :param items: an already sorted list of items, ordered by `field`
    :param field: the field of the items to compare
    """
    for index, item in enumerate(items):
        item.place = index + 1
        if index > 0:
            previous = items[index - 1]
            if getattr(previous, field) == getattr(item, field):
                item.place = previous.place


def move_player(team_bhv_id: int, old_name: str, new_name: str, log_fun: Callable = print):
    log_fun("MOVING Player: {} ({}) to {}".format(old_name, team_bhv_id, new_name))

    if old_name == new_name:
        log_fun("SKIPPING: identical names")
        return

    team_matches = models.Team.objects.filter(bhv_id=team_bhv_id)
    if not team_matches.exists():
        log_fun("SKIPPING: team not found")
        return

    team = team_matches[0]

    old_player_matches = models.Player.objects.filter(name=old_name, team=team)
    if not old_player_matches.exists():
        log_fun("SKIPPING: player not found")
        return

    old_player = old_player_matches[0]

    new_player, created = models.Player.objects.get_or_create(name=new_name, team=team)

    for score in old_player.score_set.all():
        score.player = new_player
        score.save()
    old_player.delete()
    log_fun("RENAMED Player: {} to {}".format(old_player, new_player))


def add_score(game: models.Game, team: models.Team, player_name: str, player_number: int,
              goals: int = 0, penalty_goals: int = 0, penalty_tries: int = 0,
              warning_time: str = None, first_suspension_time: str = None, second_suspension_time: str = None,
              third_suspension_time: str = None, disqualification_time: str = None, report_time: str = None,
              team_suspension_time: str = None, log_fun: Callable = print):
    log_fun('CREATING Score: {} {}'.format(game, player_name))

    divided_players = team.player_set.filter(name__regex="^{} \(\d+\)$".format(player_name))
    duplicate_scores = models.Score.objects.filter(player__name=player_name, player__team=team, game=game)
    if divided_players.exists() or duplicate_scores.exists():
        split_by_number(player_name, team)
        player_name = '{} ({})'.format(player_name, player_number)

    player, created = models.Player.objects.get_or_create(name=player_name, team=team)
    if created:
        log_fun('CREATED Player: {}'.format(player))
    else:
        log_fun('EXISTING Player: {}'.format(player))

    models.Score.objects.create(
        player=player,
        player_number=player_number,
        game=game,
        goals=goals,
        penalty_goals=penalty_goals,
        penalty_tries=penalty_tries,
        warning_time=warning_time,
        first_suspension_time=first_suspension_time,
        second_suspension_time=second_suspension_time,
        third_suspension_time=third_suspension_time,
        disqualification_time=disqualification_time,
        report_time=report_time,
        team_suspension_time=team_suspension_time
    )


@transaction.atomic
def split_by_number(original_name: str, team: models.Team, log_fun: Callable = print):
    log_fun("DIVIDING Player: {} ({})".format(original_name, team))

    matches = models.Player.objects.filter(name=original_name, team=team)
    if not matches.exists():
        log_fun("SKIPPING Player (not found): {} ({})".format(original_name, team))
        return

    original_player = matches[0]
    for score in original_player.score_set.all():
        new_name = "{} ({})".format(original_player.name, score.player_number)
        new_player, created = models.Player.objects.get_or_create(name=new_name, team=original_player.team)
        if created:
            log_fun("CREATED Player: {}".format(new_player))
        score.player = new_player
        score.save()

    if not original_player.score_set.all().exists():
        log_fun("DELETING Player (no dangling scores): {}".format(original_player))
        original_player.delete()
