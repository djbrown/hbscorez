import collections

from django.shortcuts import get_object_or_404, render

from .models import District


def detail(request, bhv_id):
    district = get_object_or_404(District, bhv_id=bhv_id)
    leagues = district.league_set
    grouped = collections.defaultdict(list)
    for league in leagues.all():
        grouped[league.season.start_year].append(league)
    sorted_groups = collections.OrderedDict(sorted(grouped.items(), key=lambda t: t[0], reverse=True))
    for leagues in sorted_groups.values():
        leagues.sort(key=lambda l: l.name)
    return render(request, 'districts/detail.j2', {'district': district, 'leagues': sorted_groups})
