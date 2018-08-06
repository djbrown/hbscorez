from django.shortcuts import render, get_object_or_404

from .models import *


def detail(request, pk):
    player = get_object_or_404(Player, pk=pk)
    scores = Score.objects.filter(player=player).order_by("game__opening_whistle")
    return render(request, 'players/detail.j2', {'player': player, 'scores': scores})
