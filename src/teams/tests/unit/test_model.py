from base.tests.base import ModelTestCase
from districts.models import District
from leagues.models import League, Season
from teams.management.commands.import_teams import create_team
from teams.models import Team


class RenamedTeam(ModelTestCase):
    def test_renamed_team(self):
        district = District.objects.create(bhv_id=4)
        season = Season.objects.create(start_year=2018)
        league = League.objects.create(
            name="League 23",
            abbreviation="L23",
            bhv_id=23,
            district=district,
            season=season,
        )

        Team.objects.create(name="Team 1", short_name="T 1", league=league, bhv_id=1)

        create_team(name="Team Eins", league=league, bhv_id=1, options={"teams": []})

        self.assert_object(Team, filters={"name": "Team Eins", "short_name": "Team Eins"})
