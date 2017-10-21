from django.shortcuts import render

from scorers.models import District


def district(request, assoc_abbr, dist_abbr):
    dist = District.objects.filter(abbreviation__iexact=dist_abbr).first()
    return render(request, 'scorers/district.html', {'district': dist})
