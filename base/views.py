import requests
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from base.models import *


def view_home(request):
    return render(request, 'base/home.html')


def view_notice(request):
    return render(request, 'base/notice.html')


def view_contact(request):
    return render(request, 'base/contact.html')


def view_associations(request):
    associations = Association.objects.all()
    return render(request, 'base/associations.html', {'associations': associations})


def view_association(request, bhv_id):
    association = get_object_or_404(Association, bhv_id=bhv_id)
    return render(request, 'base/association.html', {'association': association})


def view_district(request, bhv_id):
    district = get_object_or_404(District, bhv_id=bhv_id)
    return render(request, 'base/district.html', {'district': district})


def view_league(request, bhv_id):
    league = get_object_or_404(League, bhv_id=bhv_id)
    return render(request, 'base/league.html', {'league': league})


def view_league_players(request, bhv_id):
    league = get_object_or_404(League, bhv_id=bhv_id)
    teams = Team.objects.filter(league=league)
    players = Player.objects \
        .only('name', 'team') \
        .annotate(games=Count('score')) \
        .annotate(total_goals=Sum('score__goals')) \
        .annotate(total_penalty_goals=Sum('score__penalty_goals')) \
        .filter(total_goals__gt=0) \
        .filter(team__in=teams) \
        .order_by('-total_goals')
    return render(request, 'base/league_players.html', {'league': league, 'players': players})


def view_team(request, bhv_id):
    team = get_object_or_404(Team, bhv_id=bhv_id)
    players = Player.objects \
        .filter(team=team) \
        .only('name', 'team') \
        .annotate(games=Count('score')) \
        .annotate(total_goals=Sum('score__goals')) \
        .filter(total_goals__gt=0) \
        .annotate(total_penalty_goals=Sum('score__penalty_goals')) \
        .order_by('-total_goals')
    return render(request, 'base/team.html', {'team': team, 'players': players})


def view_player(request, pk):
    player = get_object_or_404(Player, pk=pk)
    scores = Score.objects.filter(player=player)
    print(len(scores))
    print(len(player.score_set.all()))
    return render(request, 'base/player.html', {'player': player, 'scores': scores})


def test(request):
    url = 'https://spo.handball4all.de/Spielbetrieb/index.php'
    data = {
        'orgGrpID': '28',
        'orgID': '29',
    }
    html = requests.post(url, data)
    return HttpResponse(html)
