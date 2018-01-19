from django.db.models import Count, Sum
from django.shortcuts import render, get_object_or_404

from base.models import *


def home(request):
    return render(request=request, template_name='base/home.html')


def notice(request):
    return render(request=request, template_name='base/notice.html')


def contact(request):
    return render(request=request, template_name='base/contact.html')


def associations(request):
    assocs = Association.objects.all()
    return render(request, 'base/index.html', {'associations': assocs})


def association(request, id):
    assoc = get_object_or_404(Association, pk=id)
    return render(request, 'base/association.html', {'association': assoc})


def district(request, id):
    dist = get_object_or_404(District, pk=id)
    return render(request, 'base/district.html', {'district': dist})


def league(request, id):
    league = get_object_or_404(League, pk=id)
    return render(request, 'base/league.html', {'league': league})


def league_scorers(request, id):
    league = get_object_or_404(League, pk=id)
    teams = Team.objects.filter(league=league)
    scorers = Player.objects \
        .only('name', 'team') \
        .annotate(games=Count('score')) \
        .annotate(total_goals=Sum('score__goals')) \
        .annotate(total_penalty_goals=Sum('score__penalty_goals')) \
        .filter(total_goals__gt=0) \
        .filter(team__in=teams) \
        .order_by('-total_goals')
    return render(request, 'base/scorers.html', {'league': league, 'scorers': scorers})


def team(request, id):
    team = get_object_or_404(Team, pk=id)
    scorers = Player.objects \
        .filter(team=team) \
        .only('name', 'team') \
        .annotate(games=Count('score')) \
        .annotate(total_goals=Sum('score__goals')) \
        .filter(total_goals__gt=0) \
        .annotate(total_penalty_goals=Sum('score__penalty_goals')) \
        .order_by('-total_goals')
    return render(request=request, template_name='base/team.html', context={'team': team, 'scorers': scorers})
