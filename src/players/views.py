from django.shortcuts import get_object_or_404, render

from base import logic
from players.models import Player, Score


def detail(request, key):
    player = get_object_or_404(Player, pk=key)
    scorer = logic.scorer(player)
    scores = Score.objects.filter(player=player).order_by("game__opening_whistle")
    return render(request, 'players/detail.j2', {'player': player, 'scorer': scorer, 'scores': scores})
