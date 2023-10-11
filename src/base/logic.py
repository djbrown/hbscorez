import collections
import logging
import operator

from django.db import transaction
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce, TruncMonth

from base import http, parsing
from games.models import Game, TeamOutcome
from leagues.models import League
from players.models import Player, Score
from sports_halls.models import SportsHall
from teams.models import Team

LOGGER = logging.getLogger('hbscorez')


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


def add_score(score: Score):
    LOGGER.debug('CREATING Score: %s %s', score.game, score.player.name)

    if duplicate_player_scores_exist(score):
        split_by_number(score.player.name, score.player.team)
        score.player.name = f'{score.player.name} ({score.player_number})'

    player, created = Player.objects.get_or_create(name=score.player.name, team=score.player.team)
    if created:
        LOGGER.debug('CREATED Player: %s', player)
    else:
        LOGGER.debug('EXISTING Player: %s', player)

    score.player = player
    score.save()


def duplicate_player_scores_exist(score: Score):
    divided_players = score.player.team.player_set.filter(name__regex=fr"^{score.player.name} \(\d+\)$")
    duplicate_scores = Score.objects.filter(player__name=score.player.name, player__team=score.player.team,
                                            game=score.game)
    return divided_players.exists() or duplicate_scores.exists()


def scrape_game(game_row, league: League, sports_hall: SportsHall, ignore_list: list[int] = []):
    if game_row[1].text == 'Nr.':
        LOGGER.debug('SKIPPING Row (heading)')
        return

    number = int(game_row[1].text)

    if ignore_list and number not in ignore_list:
        LOGGER.debug('SKIPPING Game (options): %s', number)
        return

    opening_whistle = parsing.parse_opening_whistle(game_row[2].text)
    home_team = Team.objects.get(league=league, short_name=game_row[4].text)
    guest_team = Team.objects.get(league=league, short_name=game_row[6].text)
    home_goals, guest_goals = parsing.parse_goals(game_row)
    report_number = parsing.parse_report_number(game_row[10])
    forfeiting_team = parsing.parse_forfeiting_team(game_row[10], home_team, guest_team)

    game = Game.objects.filter(number=number, league__season=league.season).first()
    if not game:
        game = Game.objects.create(number=number, league=league,
                                   opening_whistle=opening_whistle, sports_hall=sports_hall,
                                   home_team=home_team, guest_team=guest_team,
                                   home_goals=home_goals, guest_goals=guest_goals,
                                   report_number=report_number, forfeiting_team=forfeiting_team)
        LOGGER.info('CREATED Game: %s', game)
        return

    updated = False

    if game.home_goals != home_goals:
        game.home_goals = home_goals
        updated = True

    if game.guest_goals != guest_goals:
        game.guest_goals = guest_goals
        updated = True

    if game.report_number != report_number:
        game.report_number = report_number
        updated = True

    if updated and game.score_set:
        game.score_set.all().delete()
        LOGGER.info('DELETED Game Scores: %s', game)

    if game.opening_whistle != opening_whistle:
        game.opening_whistle = opening_whistle
        updated = True

    if game.sports_hall != sports_hall:
        game.sports_hall = sports_hall
        updated = True

    if game.forfeiting_team != forfeiting_team:
        game.forfeiting_team = forfeiting_team
        updated = True

    if updated:
        game.save()
        LOGGER.info('UPDATED Game: %s', game)
    else:
        LOGGER.debug('UNCHANGED Game: %s', game)


@transaction.atomic
def split_by_number(name: str, team: Team):
    LOGGER.info("DIVIDING Player: %s (%s)", name, team)

    player = Player.objects.filter(name=name, team=team).first()
    if not player:
        LOGGER.warning("SKIPPING Player (not found): %s (%s)", name, team)
        return

    for score in player.score_set.all():
        new_name = f"{player.name} ({score.player_number})"
        new_player, created = Player.objects.get_or_create(name=new_name, team=player.team)
        if created:
            LOGGER.debug("CREATED Player: %s", new_player)
        score.player = new_player
        score.save()

    if not player.score_set.all().exists():
        player.delete()
        LOGGER.debug("DELETED Player (no dangling scores): %s", player)


def league_games(league):
    games = league.game_set \
        .annotate(month=TruncMonth('opening_whistle')) \
        .order_by('opening_whistle')
    games_by_month = collections.defaultdict(list)
    for game in games:
        games_by_month[game.month].append(game)
    return games_by_month


def team_points(team):
    points = 0
    for game in Game.objects.filter(Q(home_team=team) | Q(guest_team=team)):
        outcome = game.outcome_for(team)
        if outcome == TeamOutcome.WIN:
            points += 2
        elif outcome == TeamOutcome.TIE:
            points += 1
    return points


def top_league_teams(league):
    teams = league.team_set.all()
    for team in teams:
        team.points = team_points(team)
    teams = sorted(teams, key=operator.attrgetter('points'), reverse=True)
    add_ranking_place(teams, 'points')
    teams_by_rank = collections.defaultdict(list)
    for team in teams:
        if team.place <= 5:
            teams_by_rank[team.place].append(team)
    for team_group in teams_by_rank.values():
        team_group.sort(key=lambda p: p.name)
    return teams_by_rank


def scorer(player: Player):
    return Player.objects.filter(pk=player.pk) \
        .annotate(games=Count('score')) \
        .annotate(total_goals=Coalesce(Sum('score__goals'), 0)) \
        .annotate(total_penalty_tries=Sum('score__penalty_tries')) \
        .annotate(total_penalty_goals=Sum('score__penalty_goals')) \
        .annotate(total_field_goals=F('total_goals') - F('total_penalty_goals')) \
        .first()


def league_scorers(league):
    scorers = Player.objects \
        .filter(team__league=league) \
        .annotate(games=Count('score')) \
        .filter(games__gt=0) \
        .annotate(total_goals=Coalesce(Sum('score__goals'), 0)) \
        .filter(total_goals__gt=0) \
        .annotate(total_penalty_goals=Sum('score__penalty_goals')) \
        .annotate(total_field_goals=F('total_goals') - F('total_penalty_goals')) \
        .order_by('-total_goals')
    add_ranking_place(scorers, 'total_goals')
    return scorers


def top_league_scorers(league):
    players = Player.objects \
        .filter(team__league=league) \
        .annotate(games=Count('score')) \
        .filter(games__gt=0) \
        .annotate(total_goals=Coalesce(Sum('score__goals'), 0)) \
        .order_by('-total_goals')
    add_ranking_place(players, 'total_goals')
    scorers_by_rank = collections.defaultdict(list)
    for player in players:
        if player.place <= 5:
            scorers_by_rank[player.place].append(player)
    for scorers_group in scorers_by_rank.values():
        scorers_group.sort(key=lambda p: p.name)
    return scorers_by_rank


def league_offenders(league):
    offenders = Player.objects \
        .filter(team__league=league) \
        .annotate(games=Count('score')) \
        .annotate(warnings=Count('score__warning_time')) \
        .annotate(suspensions=Count('score__first_suspension_time') +
                  Count('score__second_suspension_time') +
                  Count('score__third_suspension_time')) \
        .annotate(disqualifications=Count('score__disqualification_time')) \
        .annotate(offender_points=F('warnings') + 2 * F('suspensions') + 3 * F('disqualifications')) \
        .filter(offender_points__gt=0) \
        .order_by('-offender_points')
    add_ranking_place(offenders, 'offender_points')
    return offenders


def top_league_offenders(league):
    offenders = league_offenders(league)
    offenders_by_place = collections.defaultdict(list)
    for offender in offenders:
        if offender.place <= 5:
            offenders_by_place[offender.place].append(offender)
    for scorers_group in offenders_by_place.values():
        scorers_group.sort(key=lambda p: p.name)
    return offenders_by_place


def scrape_sports_hall(game_row, processed: set[int] = set()):
    if len(game_row[3]) != 1:
        return None
    link = game_row[3][0]
    number = int(link.text)
    bhv_id = parsing.parse_sports_hall_bhv_id(link)

    sports_hall = SportsHall.objects.filter(number=number, bhv_id=bhv_id).first()
    if bhv_id in processed:
        LOGGER.debug('SKIPPING Sports Hall: %s (already processed)', sports_hall)
        return sports_hall

    url = SportsHall.build_source_url(bhv_id)
    html = http.get_text(url)
    dom = parsing.html_dom(html)
    table = parsing.parse_sports_hall_table(dom)

    name = parsing.parse_sports_hall_name(table)
    address = parsing.parse_sports_hall_address(table)
    phone_number = parsing.parse_sports_hall_phone_number(table)
    latitude, longitude = parsing.parse_sports_hall_coordinates(dom)

    if not sports_hall:
        sports_hall = SportsHall.objects.create(number=number, name=name, address=address,
                                                phone_number=phone_number, latitude=latitude,
                                                longitude=longitude, bhv_id=bhv_id)
        LOGGER.info('CREATED Sports Hall: %s', sports_hall)
        return sports_hall

    updated = False

    if sports_hall.name != name:
        sports_hall.name = name
        updated = True

    if sports_hall.address != address:
        sports_hall.address = address
        updated = True

    if sports_hall.phone_number != phone_number:
        sports_hall.phone_number = phone_number
        updated = True

    if sports_hall.latitude != latitude:
        sports_hall.latitude = latitude
        updated = True

    if sports_hall.longitude != longitude:
        sports_hall.longitude = longitude
        updated = True

    if updated:
        sports_hall.save()
        LOGGER.info('UPDATED Sports Hall: %s', sports_hall)
    else:
        LOGGER.debug('UNCHANGED Sports Hall: %s', sports_hall)

    return sports_hall
