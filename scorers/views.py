from django.db.models import Sum, Count
from django.shortcuts import render

from scorers.models import Score


def index(request):
    scores = Score.objects \
        .values('player_name', 'club__name') \
        .annotate(total=Sum('goals')) \
        .filter(total__gt=0) \
        .annotate(scores=Count('player_name')) \
        .annotate(penalties=Sum('penalty_goals')) \
        .order_by('-total')
    return render(request, 'scorers/scorers.html', {'scores': scores})
