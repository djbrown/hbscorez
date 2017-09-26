from django.db.models import Sum, Count
from django.shortcuts import render

from scorers.models import PlayerScore


def index(request):
    scores = PlayerScore.objects \
        .values('player_name') \
        .annotate(total=Sum('goals')) \
        .filter(total__gt=0) \
        .annotate(scores=Count('player_name')) \
        .annotate(penalties=Sum('penalty_goals')) \
        .order_by('-total')
    return render(request, 'scorers/scorers.html', {'scores': scores})
