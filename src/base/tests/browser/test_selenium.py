from selenium.webdriver.common.by import By

from base.tests.base import BrowserTestCase


class TestSelenium(BrowserTestCase):

    def test_internet_connection(self):
        self.driver.get('https://saucelabs.com/test/guinea-pig')
        self.assertEqual('I am a page title - Sauce Labs', self.driver.title)
        body = self.driver.find_element(By.CSS_SELECTOR, 'body')
        self.assertIn('This page is a Selenium sandbox', body.text)

    def test_body_exists(self):
        driver = self.driver
        driver.get(self.live_server_url)
        body = driver.find_element(By.TAG_NAME, 'body')
        self.assertIsNotNone(body)

    def test_w3_org_exists(self):
        driver = self.driver
        driver.get('https://www.w3.org/')
        body = driver.find_element(By.ID, 'www-w3-org')
        self.assertIsNotNone(body)
