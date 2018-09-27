from django.http import JsonResponse

from associations.models import Association
from districts.models import District
from leagues.models import League, Season


def associations(_):
    associations = [{
        'bhvId': a.bhv_id,
        'name': a.name,
        'abbreviation': a.abbreviation,
    } for a in Association.objects.all()]

    return JsonResponse({'associations': associations})


def association_districts(_, bhv_id):
    associations = Association.objects.filter(bhv_id=bhv_id)

    if not associations.exists():
        return JsonResponse({'error': 'No matching Association found.'}, status=404)

    association = associations[0]

    districts = [{
        'bhvId': district.bhv_id,
        'name': district.name,
    } for district in association.district_set.all()]

    return JsonResponse({'districts': districts})


def district_seasons(_, bhv_id):
    districts = District.objects.filter(bhv_id=bhv_id)

    if not districts.exists():
        return JsonResponse({'error': 'No matching District found.'}, status=404)

    district = districts[0]

    seasons = [{
        'startYear': s.season.start_year
    } for s in district.league_set.all()]

    return JsonResponse({'seasons': seasons})


def district_season_leagues(_, bhv_id, start_year):
    districts = District.objects.filter(bhv_id=bhv_id)
    if not districts.exists():
        return JsonResponse({'error': 'No matching District found.'}, status=404)
    district = districts[0]

    seasons = Season.objects.filter(start_year=start_year)
    if not seasons.exists():
        return JsonResponse({'error': 'No matching Season found.'}, status=404)
    season = seasons[0]

    leagues = [{
        'bhvId': league.bhv_id,
        'name': league.name,
    } for league in League.objects.filter(district=district, season=season)]

    return JsonResponse({'leagues': leagues})


def league_teams(_, bhv_id):
    leagues = League.objects.filter(bhv_id=bhv_id)

    if not leagues.exists():
        return JsonResponse({'error': 'No matching League found.'}, status=404)

    league = leagues[0]

    teams = [{
        'bhvId': team.bhv_id,
        'name': team.name,
        'shortName': team.short_name,
    } for team in league.team_set.all()]

    return JsonResponse({'teams': teams})
