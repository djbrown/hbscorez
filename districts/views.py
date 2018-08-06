from django.shortcuts import render, get_object_or_404

from .models import District


def detail(request, bhv_id):
    district = get_object_or_404(District, bhv_id=bhv_id)
    return render(request, 'districts/detail.j2', {'district': district})
