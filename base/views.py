from django.db.models import Count, Sum
from django.http import Http404
from django.shortcuts import render, get_object_or_404

from scorers.models import Team, Player


def home(request):
    return render(request=request, template_name='base/home.html')


def notice(request):
    return render(request=request, template_name='base/notice.html')


def contact(request):
    return render(request=request, template_name='base/contact.html')


def team(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    scorers = Player.objects \
        .filter(team=team) \
        .only('name', 'team') \
        .annotate(games=Count('score')) \
        .annotate(total_goals=Sum('score__goals')) \
        .filter(total_goals__gt=0) \
        .annotate(total_penalty_goals=Sum('score__penalty_goals')) \
        .order_by('-total_goals')
    return render(request=request, template_name='base/team.html', context={'team': team, 'scorers': scorers})
