from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from associations.models import Association
from base.tests.base import BrowserTestCase
from districts.models import District
from leagues.models import League, Season
from players.models import Player
from teams.models import Team


class TestLink(BrowserTestCase):
    def test_link(self):
        association = Association.objects.create(
            name="Test Association 10", abbreviation="A10", bhv_id=10, source_url=""
        )
        district = District.objects.create(name="Test District 20", bhv_id=20)
        association.district_set.add(district)
        season = Season.objects.create(start_year=2026)
        lg = League.objects.create(name="Test L 30", abbreviation="L30", bhv_id=30, district=district, season=season)
        team = Team.objects.create(name="Test Team 40", short_name="T40", bhv_id=40, league=lg)
        player = Player.objects.create(name="John Lennon", team=team)
        username = "john"
        password = "johnpassword"
        User.objects.create_user(username, "lennon@thebeatles.com", password)

        self.navigate("users:login")
        username_textfield = self.driver.find_element(By.NAME, "username")
        username_textfield.send_keys(username)
        password_textfield = self.driver.find_element(By.NAME, "password")
        password_textfield.send_keys(password)
        with self.wait():
            password_textfield.submit()

        self.navigate("users:profile")
        link_items = self.driver.find_elements(By.CSS_SELECTOR, "h5 + ul > li")
        self.assertEqual(len(link_items), 0)

        self.navigate("users:link")
        Select(self.driver.find_element(By.ID, "associations")).select_by_value(str(association.pk))
        Select(self.driver.find_element(By.ID, "districts")).select_by_value(str(district.pk))
        Select(self.driver.find_element(By.ID, "seasons")).select_by_value(str(season.start_year))
        Select(self.driver.find_element(By.ID, "leagues")).select_by_value(str(lg.pk))
        Select(self.driver.find_element(By.ID, "teams")).select_by_value(str(team.pk))
        (name_element := self.driver.find_element(By.ID, "name")).send_keys(player.name)
        self.driver.find_element(By.ID, "consent-identity").click()
        self.driver.find_element(By.ID, "consent-delete").click()
        self.driver.find_element(By.ID, "consent-publish").click()
        with self.wait():
            name_element.submit()

        self.assert_view("users:profile")
        link_items = self.driver.find_elements(By.CSS_SELECTOR, "h5 + ul > li")
        self.assertEqual(len(link_items), 1)
