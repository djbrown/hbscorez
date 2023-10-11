
from decimal import Decimal
from pathlib import Path

from django.conf import settings

from base import logic, parsing
from base.tests.base import IntegrationTestCase
from sports_halls.models import SportsHall


def read_html(file_name):
    file: Path = settings.ROOT_DIR / 'src' / 'games' / 'tests' / file_name
    content = file.read_text()
    return parsing.html_dom(content)


class Update(IntegrationTestCase):
    def test_update(self):
        dom = read_html('game_table_single_game.html')
        [game_row] = parsing.parse_game_rows(dom)
        SportsHall.objects.create(number=22010, name="My Gym", address="addr", phone_number="tel",
                                  latitude="10", longitude="20", bhv_id=487)

        logic.scrape_sports_hall(game_row)
        sports_hall = self.assert_objects(SportsHall)

        self.assertEqual(sports_hall.name, "Rebland-Halle")
        self.assertEqual(sports_hall.address, "Unterer Jagdweg 69, D 69254 Malsch")
        self.assertEqual(sports_hall.phone_number, "07253-24150")
        self.assertEqual(sports_hall.latitude, Decimal('49.2494'))
        self.assertEqual(sports_hall.longitude, Decimal('8.6917'))
