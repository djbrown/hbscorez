from collections import defaultdict

from django.shortcuts import get_object_or_404, render

from clubs.models import Club
from teams.models import Team


def detail(request, bhv_id):
    club = get_object_or_404(Club, bhv_id=bhv_id)
    teams_by_season = defaultdict(list)
    team: Team
    for team in club.team_set.order_by("-league__season__start_year", "name", "league__abbreviation"):
        teams_by_season[team.league.season.start_year].append(team)
    return render(request, "clubs/detail.j2", {"club": club, "teams_by_season": teams_by_season})
