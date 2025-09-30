from base.tests.base import IntegrationTestCase
from games.models import Team


class TeamTest(IntegrationTestCase):
    def test_update(self):
        self.assert_command("import_associations", "-a", 80)
        self.assert_command("import_clubs", "-a", 80, "-c", 213031)
        self.assert_command("import_districts", "-d", 80)
        self.assert_command("import_leagues", "-s", 2023, "-l", 109051)

        self.assert_object(Team, filters={"bhv_id": 1036036, "club__bhv_id": 213031})
