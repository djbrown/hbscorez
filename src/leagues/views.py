from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from base import logic
from base.logic import add_ranking_place

from .models import League


def detail(request, bhv_id):
    league = get_object_or_404(League, bhv_id=bhv_id)
    top_teams = logic.top_league_teams(league)
    top_league_scorers = logic.top_league_scorers(league)
    top_league_offenders = logic.top_league_offenders(league)
    games_count = league.game_set.filter(home_team__retirement__isnull=True,
                                         guest_team__retirement__isnull=True).count()
    games_staged = league.game_set.filter(home_goals__isnull=False, guest_goals__isnull=False).count()
    games_progress = games_staged / games_count if games_count > 0 else 0
    return render(request, 'leagues/detail.j2', {
        'league': league,
        'games_count': games_count,
        'games_staged': games_staged,
        'teams': top_teams,
        'scorers': top_league_scorers,
        'offenders': top_league_offenders,
        'games_progress': games_progress,
    })


def teams(request, bhv_id):
    league = get_object_or_404(League, bhv_id=bhv_id)
    return render(request, 'leagues/teams.j2', {
        'league': league,
    })


def games(request, bhv_id):
    league = get_object_or_404(League, bhv_id=bhv_id)
    games_by_month = logic.league_games(league)
    return render(request, 'leagues/games.j2', {
        'league': league,
        'games_by_month': games_by_month,
    })


def scorers(request, bhv_id):
    league = get_object_or_404(League, bhv_id=bhv_id)
    league_scorers = logic.league_scorers(league)
    return render(request, 'leagues/scorers.j2', {
        'league': league,
        'scorers': league_scorers,
    })


def offenders(request, bhv_id):
    league = get_object_or_404(League, bhv_id=bhv_id)
    league_offenders = logic.league_offenders(league)
    add_ranking_place(league_offenders, 'offender_points')
    return render(request, 'leagues/offenders.j2', {
        'league': league,
        'offenders': league_offenders,
    })


def calendar():
    return HttpResponse(status=501)
