from django.shortcuts import get_object_or_404, render

from clubs.models import Club


def detail(request, bhv_id):
    club = get_object_or_404(Club, bhv_id=bhv_id)
    return render(request, 'clubs/detail.j2', {'club': club})
