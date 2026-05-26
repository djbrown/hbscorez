import collections

from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_safe

from districts.models import District


@require_safe
def detail(request, pk):
    district = get_object_or_404(District, pk=pk)
    leagues = district.league_set
    grouped = collections.defaultdict(list)
    for league in leagues.all():
        grouped[league.season.start_year].append(league)
    sorted_groups = collections.OrderedDict(sorted(grouped.items(), key=lambda t: t[0], reverse=True))
    for leagues in sorted_groups.values():
        leagues.sort(key=lambda league: league.abbreviation)
    return render(request, "districts/detail.j2", {"district": district, "leagues": sorted_groups})
