from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_safe

from base import logic
from base.logic import add_ranking_place
from leagues.models import League


@require_safe
def detail(request, pk):
    league = get_object_or_404(League, pk=pk)
    top_teams = logic.top_league_teams(league)
    top_league_scorers = logic.top_league_scorers(league)
    top_league_offenders = logic.top_league_offenders(league)
    games_count = league.game_set.filter(
        home_team__retirement__isnull=True, guest_team__retirement__isnull=True
    ).count()
    games_staged = league.game_set.filter(home_goals__isnull=False, guest_goals__isnull=False).count()
    games_progress = games_staged / games_count if games_count > 0 else 0
    return render(
        request,
        "leagues/detail.j2",
        {
            "league": league,
            "games_count": games_count,
            "games_staged": games_staged,
            "teams": top_teams,
            "scorers": top_league_scorers,
            "offenders": top_league_offenders,
            "games_progress": games_progress,
        },
    )


@require_safe
def teams(request, pk):
    league = get_object_or_404(League, pk=pk)
    return render(request, "leagues/teams.j2", {"league": league})


@require_safe
def games(request, pk):
    league = get_object_or_404(League, pk=pk)
    games_by_month = logic.league_games(league)
    return render(request, "leagues/games.j2", {"league": league, "games_by_month": games_by_month})


@require_safe
def scorers(request, pk):
    league = get_object_or_404(League, pk=pk)
    league_scorers = logic.league_scorers(league)
    return render(request, "leagues/scorers.j2", {"league": league, "scorers": league_scorers})


@require_safe
def offenders(request, pk):
    league = get_object_or_404(League, pk=pk)
    league_offenders = logic.league_offenders(league)
    add_ranking_place(league_offenders, "offender_points")
    return render(request, "leagues/offenders.j2", {"league": league, "offenders": league_offenders})
