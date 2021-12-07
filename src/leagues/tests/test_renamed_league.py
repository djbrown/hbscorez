from base.tests.base import ModelTestCase
from districts.models import District
from leagues.models import League, Season
from teams.models import Team


class RenamedTeam(ModelTestCase):
    def test_renamed_team(self):
        district = District.objects.create(bhv_id=4)
        season = Season.objects.create(start_year=2018)
        league = League.objects.create(name='League 23', abbreviation='L23',
                                       bhv_id=23, district=district, season=season)

        Team.objects.create(name='Team 1', short_name='T 1', league=league, bhv_id=1)

        Team.create_or_update_team('Team Eins', 'Team E', league, 1)

        self.assert_objects(Team, filters={"name": 'Team Eins', "short_name": 'Team E'})
