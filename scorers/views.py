from django.db.models import Sum, Count
from django.shortcuts import render

from scorers.models import Club, Player


def index(request):
    scorers = Player.objects \
        .only('name', 'club') \
        .annotate(games=Count('score')) \
        .annotate(total_goals=Sum('score__goals')) \
        .annotate(total_penalty_goals=Sum('score__penalty_goals')) \
        .filter(total_goals__gt=0) \
        .order_by('-total_goals')
    return render(request, 'scorers/scorers.html', {'scorers': scorers})
