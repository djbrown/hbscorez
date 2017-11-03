from django.db.models import Count, Sum
from django.shortcuts import render

from associations.models import Association
from districts.models import District
from leagues.models import League
from scorers.models import Team, Player


def league(request, assoc_abbr, dist_abbr, league_abbr):
    district = District.objects.filter(abbreviation__iexact=dist_abbr.upper()).first()
    league = League.objects.filter(abbreviation__iexact=league_abbr.upper(), district=district).first()
    return render(request, 'scorers/league.html', {'league': league})


def league_scorers(request, assoc_abbr, dist_abbr, league_abbr):
    association = Association.objects.filter(abbreviation__iexact=assoc_abbr.upper()).first()
    district = District.objects.filter(abbreviation__iexact=dist_abbr.upper(), association=association).first()
    league = League.objects.filter(abbreviation__iexact=league_abbr.upper(), district=district).first()
    teams = Team.objects.filter(league=league)
    scorers = Player.objects \
        .only('name', 'team') \
        .annotate(games=Count('score')) \
        .annotate(total_goals=Sum('score__goals')) \
        .annotate(total_penalty_goals=Sum('score__penalty_goals')) \
        .filter(total_goals__gt=0) \
        .filter(team__in=teams) \
        .order_by('-total_goals')
    return render(request, 'scorers/scorers.html', {'league': league, 'scorers': scorers})
