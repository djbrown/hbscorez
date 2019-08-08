from django.http import JsonResponse

from associations.models import Association
from districts.models import District
from leagues.models import League, Season


def associations(_):
    light_associations = [{
        'bhvId': a.bhv_id,
        'name': a.name,
        'abbreviation': a.abbreviation,
    } for a in Association.objects.all()]

    return JsonResponse({'associations': light_associations})


def association_districts(_, bhv_id):
    association_results = Association.objects.filter(bhv_id=bhv_id)

    if not association_results.exists():
        return JsonResponse({'error': 'No matching Association found.'}, status=404)

    association = association_results[0]

    districts = [{
        'bhvId': district.bhv_id,
        'name': district.name,
    } for district in association.district_set.all()]

    return JsonResponse({'districts': districts})


def seasons(_):
    light_seasons = [{
        'startYear': season.start_year
    } for season in Season.objects.all()]

    return JsonResponse({'seasons': light_seasons})


def district_season_leagues(_, bhv_id, start_year):
    district_results = District.objects.filter(bhv_id=bhv_id)
    if not district_results.exists():
        return JsonResponse({'error': 'No matching District found.'}, status=404)
    district = district_results[0]

    season_results = Season.objects.filter(start_year=start_year)
    if not season_results.exists():
        return JsonResponse({'error': 'No matching Season found.'}, status=404)
    season = season_results[0]

    light_leagues = [{
        'bhvId': league.bhv_id,
        'name': league.name,
    } for league in League.objects.filter(district=district, season=season)]

    return JsonResponse({'leagues': light_leagues})


def league_teams(_, bhv_id):
    leagues = League.objects.filter(bhv_id=bhv_id)

    if not leagues.exists():
        return JsonResponse({'error': 'No matching League found.'}, status=404)

    league = leagues[0]

    light_teams = [{
        'bhvId': team.bhv_id,
        'name': team.name,
        'shortName': team.short_name,
    } for team in league.team_set.all()]

    return JsonResponse({'teams': light_teams})
