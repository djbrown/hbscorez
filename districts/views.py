from django.shortcuts import render

from associations.models import Association
from districts.models import District


def district(request, assoc_abbr, dist_abbr):
    association = Association.objects.filter(abbreviation=assoc_abbr.upper()).first()
    dist = District.objects.filter(abbreviation=dist_abbr.upper(), association=association).first()
    return render(request, 'scorers/district.html', {'district': dist})
