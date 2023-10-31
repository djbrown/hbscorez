from pathlib import Path

import tabula

from base.tests.base import ModelTestCase
from districts.models import District
from games.models import Game
from leagues.models import League, Season
from players.management.commands.parse_report import import_score, import_scores
from players.models import Player, Score
from teams.models import Team


class NonameTest(ModelTestCase):
    def test_specific(self):
        district = District.objects.create(name="District", bhv_id=1)
        season = Season.objects.create(start_year=2023)
        league = League.objects.create(name="League", abbreviation="LEAGUE", district=district, season=season, bhv_id=1)
        home_team = Team.objects.create(name="Home Team", short_name="HOME", league=league, bhv_id=1)
        guest_team = Team.objects.create(name="Guest Team",  short_name="GUEST", league=league, bhv_id=2)
        game = Game.objects.create(number=1, league=league, home_team=home_team, guest_team=guest_team)

        path = Path(__file__).parent / 'report-with-nonames.pdf'
        table = tabula.read_pdf(path, output_format='json', pages=2, lattice=True)[0]

        import_score(table['data'][5], game, home_team)

        self.assert_objects(Score)
        self.assert_objects(Player, 0)

    def test_preexisting(self):
        district = District.objects.create(name="District", bhv_id=1)
        season = Season.objects.create(start_year=2023)
        league = League.objects.create(name="League", abbreviation="LEAGUE", district=district, season=season, bhv_id=1)
        home_team = Team.objects.create(name="Home Team", short_name="HOME", league=league, bhv_id=1)
        guest_team = Team.objects.create(name="Guest Team",  short_name="GUEST", league=league, bhv_id=2)
        game = Game.objects.create(number=1, league=league, home_team=home_team, guest_team=guest_team)

        Player.objects.create(name="N.N. N.N.", team=home_team)

        path = Path(__file__).parent / 'report-with-nonames.pdf'
        table = tabula.read_pdf(path, output_format='json', pages=2, lattice=True)[0]

        import_score(table['data'][5], game, home_team)

        self.assert_objects(Score)
        self.assert_objects(Player)

    def test_multiple(self):
        district = District.objects.create(name="District", bhv_id=1)
        season = Season.objects.create(start_year=2023)
        league = League.objects.create(name="League", abbreviation="LEAGUE", district=district, season=season, bhv_id=1)
        home_team = Team.objects.create(name="Home Team", short_name="HOME", league=league, bhv_id=1)
        guest_team = Team.objects.create(name="Guest Team",  short_name="GUEST", league=league, bhv_id=2)
        game = Game.objects.create(number=1, league=league, home_team=home_team, guest_team=guest_team)

        path = Path(__file__).parent / 'report-with-nonames.pdf'
        table = tabula.read_pdf(path, output_format='json', pages=2, lattice=True)[0]

        import_scores(table, game, home_team)

        self.assert_objects(Score, 14)
        self.assert_objects(Score, 3, filters={'player__isnull': True})


class ReassignedNumberTest(ModelTestCase):
    def test_specific(self):
        district = District.objects.create(name="District", bhv_id=1)
        season = Season.objects.create(start_year=2023)
        league = League.objects.create(name="League", abbreviation="LEAGUE", district=district, season=season, bhv_id=1)
        home_team = Team.objects.create(name="Home Team", short_name="HOME", league=league, bhv_id=1)
        guest_team = Team.objects.create(name="Guest Team",  short_name="GUEST", league=league, bhv_id=2)
        game = Game.objects.create(number=1, league=league, home_team=home_team, guest_team=guest_team)
        self.assert_objects(Player, count=0)

        path = Path(__file__).parent / 'report-with-reassigned-numbers.pdf'
        table = tabula.read_pdf(path, output_format='json', pages=2, lattice=True)[0]
        row = table['data'][9]

        import_score(row, game, home_team)

        player = self.assert_objects(Player)
        self.assertEqual(player.name, "Tobias Emmerich")

    def test_preexisting(self):
        district = District.objects.create(name="District", bhv_id=1)
        season = Season.objects.create(start_year=2023)
        league = League.objects.create(name="League", abbreviation="LEAGUE", district=district, season=season, bhv_id=1)
        home_team = Team.objects.create(name="Home Team", short_name="HOME", league=league, bhv_id=1)
        guest_team = Team.objects.create(name="Guest Team",  short_name="GUEST", league=league, bhv_id=2)
        game = Game.objects.create(number=1, league=league, home_team=home_team, guest_team=guest_team)

        Player.objects.create(name="Tobias Emmerich", team=home_team)

        path = Path(__file__).parent / 'report-with-reassigned-numbers.pdf'
        table = tabula.read_pdf(path, output_format='json', pages=2, lattice=True)[0]
        row = table['data'][9]

        import_score(row, game, home_team)

        player = self.assert_objects(Player)
        self.assertEqual(player.name, "Tobias Emmerich")

    def test_lengthy_reassigned(self):
        district = District.objects.create(name="District", bhv_id=1)
        season = Season.objects.create(start_year=2023)
        league = League.objects.create(name="League", abbreviation="LEAGUE", district=district, season=season, bhv_id=1)
        home_team = Team.objects.create(name="Home Team", short_name="HOME", league=league, bhv_id=1)
        guest_team = Team.objects.create(name="Guest Team",  short_name="GUEST", league=league, bhv_id=2)
        game = Game.objects.create(number=1, league=league, home_team=home_team, guest_team=guest_team)

        Player.objects.create(name="Fabian Rotermund", team=home_team)

        path = Path(__file__).parent / 'report-with-reassigned-lengthy-name.pdf'
        table = tabula.read_pdf(path, output_format='json', pages=2, lattice=True)[0]
        row = table['data'][11]

        import_score(row, game, home_team)

        player = self.assert_objects(Player)
        self.assertEqual(player.name, "Fabian Rotermund")
