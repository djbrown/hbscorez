from django.shortcuts import get_object_or_404, render

from .models import Player, Score


def detail(request, pk):
    player = get_object_or_404(Player, pk=pk)
    scores = Score.objects.filter(player=player).order_by("game__opening_whistle")
    return render(request, 'players/detail.j2', {'player': player, 'scores': scores})
