from django.db.models import Count, Sum
from django.shortcuts import render

from scorers.models import District, Association, League, Player, Team


def index(request):
    associations = Association.objects.all()
    return render(request, 'scorers/index.html', {'associations': associations})


def association_overview(request, assoc_abbr):
    association = Association.objects.filter(abbreviation__iexact=assoc_abbr).first()
    return render(request, 'scorers/association.html', {'association': association})


def district_overview(request, assoc_abbr, dist_abbr):
    district = District.objects.filter(abbreviation__iexact=dist_abbr).first()
    return render(request, 'scorers/district.html', {'district': district})


def league_overview(request, assoc_abbr, dist_abbr, league_abbr):
    district = District.objects.filter(abbreviation__iexact=dist_abbr).first()
    league = League.objects.filter(abbreviation__iexact=league_abbr, district=district).first()
    return render(request, 'scorers/league.html', {'league': league})


def league_scorers(request, assoc_abbr, dist_abbr, league_abbr):
    association = Association.objects.filter(abbreviation__iexact=assoc_abbr).first()
    district = District.objects.filter(abbreviation__iexact=dist_abbr, association=association).first()
    league = League.objects.filter(abbreviation__iexact=league_abbr, district=district).first()
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
