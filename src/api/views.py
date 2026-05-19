from django.http import JsonResponse

from associations.models import Association
from districts.models import District
from leagues.models import League, Season


def associations(_):
    light_associations = [
        {
            "pk": a.pk,
            "name": a.name,
            "abbreviation": a.abbreviation,
        }
        for a in Association.objects.all()
    ]

    return JsonResponse({"associations": light_associations})


def association_districts(_, pk):
    association_results = Association.objects.filter(pk=pk)

    if not association_results.exists():
        return JsonResponse({"error": "No matching Association found."}, status=404)

    association = association_results[0]

    districts = [
        {
            "pk": district.pk,
            "name": district.name,
        }
        for district in association.district_set.all()
    ]

    return JsonResponse({"districts": districts})


def seasons(_):
    light_seasons = [{"startYear": season.start_year} for season in Season.objects.all()]

    return JsonResponse({"seasons": light_seasons})


def district_season_leagues(_, pk, start_year):
    district_results = District.objects.filter(pk=pk)
    if not district_results.exists():
        return JsonResponse({"error": "No matching District found."}, status=404)
    district = district_results[0]

    season_results = Season.objects.filter(start_year=start_year)
    if not season_results.exists():
        return JsonResponse({"error": "No matching Season found."}, status=404)
    season = season_results[0]

    light_leagues = [
        {
            "pk": league.pk,
            "name": league.name,
        }
        for league in League.objects.filter(district=district, season=season)
    ]

    return JsonResponse({"leagues": light_leagues})


def league_teams(_, pk):
    leagues = League.objects.filter(pk=pk)

    if not leagues.exists():
        return JsonResponse({"error": "No matching League found."}, status=404)

    league = leagues[0]

    light_teams = [
        {
            "pk": team.pk,
            "name": team.name,
            "shortName": team.short_name,
        }
        for team in league.team_set.all()
    ]

    return JsonResponse({"teams": light_teams})
