from django.db.models import Count, Sum, F
from django.db.models.functions import TruncMonth, Coalesce
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from base.logic import add_ranking_place
from players.models import Player
from .models import League


def detail(request, bhv_id):
    league = get_object_or_404(League, bhv_id=bhv_id)
    return render(request, 'leagues/detail.html', {'league': league})


def teams(request, bhv_id):
    league = get_object_or_404(League, bhv_id=bhv_id)
    return render(request, 'leagues/teams.html', {'league': league})


def games(request, bhv_id):
    league = get_object_or_404(League, bhv_id=bhv_id)
    games = league.game_set \
        .annotate(month=TruncMonth('opening_whistle')) \
        .order_by('opening_whistle')
    games_by_month = {}
    for game in games:
        games_by_month.setdefault(game.month, []).append(game)
    return render(request, 'leagues/games.html',
                  {'league': league, 'games_by_month': games_by_month})


def scorers(request, bhv_id):
    league = get_object_or_404(League, bhv_id=bhv_id)
    players = Player.objects \
        .filter(team__league=league) \
        .annotate(games=Count('score')) \
        .filter(games__gt=0) \
        .annotate(total_goals=Coalesce(Sum('score__goals'), 0)) \
        .filter(total_goals__gt=0) \
        .annotate(total_penalty_goals=Sum('score__penalty_goals')) \
        .annotate(total_field_goals=F('total_goals') - F('total_penalty_goals')) \
        .order_by('-total_goals')
    add_ranking_place(players, 'total_goals')
    return render(request, 'leagues/scorers.html', {'league': league, 'players': players})


def penalties(request, bhv_id):
    league = get_object_or_404(League, bhv_id=bhv_id)
    players = Player.objects \
        .filter(team__league=league) \
        .annotate(games=Count('score')) \
        .annotate(warnings=Count('score__warning_time')) \
        .annotate(suspensions=
                  Count('score__first_suspension_time') +
                  Count('score__second_suspension_time') +
                  Count('score__third_suspension_time')) \
        .annotate(disqualifications=Count('score__disqualification_time')) \
        .annotate(penalty_points=F('warnings') + 2 * F('suspensions') + 3 * F('disqualifications')) \
        .filter(penalty_points__gt=0) \
        .order_by('-penalty_points')
    add_ranking_place(players, 'penalty_points')
    return render(request, 'leagues/penalties.html', {'league': league, 'players': players})


def calendar(request, bhv_id):
    return HttpResponse(status=501)
