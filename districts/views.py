from django.shortcuts import render

from districts.models import District


def district(request, assoc_abbr, dist_abbr):
    dist = District.objects.filter(abbreviation=dist_abbr.upper()).first()
    return render(request, 'scorers/district.html', {'district': dist})
