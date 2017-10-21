from django.shortcuts import render

from districts.models import District
from leagues.models import League


def league(request, assoc_abbr, dist_abbr, league_abbr):
    district = District.objects.filter(abbreviation__iexact=dist_abbr).first()
    l = League.objects.filter(abbreviation__iexact=league_abbr, district=district).first()
    return render(request, 'scorers/league.html', {'league': l})
