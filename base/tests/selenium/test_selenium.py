from unittest import skip

from selenium.webdriver.common.keys import Keys

from base.tests.base import SeleniumTestCase


class TestSelenium(SeleniumTestCase):
    def test_internet_connection(self):
        self.driver.get('https://saucelabs.com/test/guinea-pig')
        self.assertEqual('I am a page title - Sauce Labs', self.driver.title)
        body = self.driver.find_element_by_css_selector('body')
        self.assertIn('This page is a Selenium sandbox', body.text)


# @skip("generates error code 502 bad gatewey in sauce labs")
    def test_navbar_exists(self):
        driver = self.driver
        driver.get(self.live_server_url)
        nav = driver.find_element_by_id('navbar')
        self.assertIsNotNone(nav)

    def test_w3_org_exists(self):
        driver = self.driver
        driver.get('https://www.w3.org/')
        body = driver.find_element_by_id('www-w3-org')
        self.assertIsNotNone(body)

    @skip("Register page not implemented yet")
    def test_register(self):
        driver = self.driver

        # Opening the link we want to test
        driver.get('http://127.0.0.1:8000/accounts/register/')

        # find the form element
        first_name = driver.find_element_by_id('id_first_name')
        last_name = driver.find_element_by_id('id_last_name')
        username = driver.find_element_by_id('id_username')
        email = driver.find_element_by_id('id_email')
        password1 = driver.find_element_by_id('id_password1')
        password2 = driver.find_element_by_id('id_password2')

        submit = driver.find_element_by_name('register')

        # Fill the form with data
        first_name.send_keys('Homer')
        last_name.send_keys('Simpson')
        username.send_keys('duffman')
        email.send_keys('homer@simpson.com')
        password1.send_keys('123456')
        password2.send_keys('123456')

        # submitting the form
        submit.send_keys(Keys.RETURN)

        # check the returned result
        assert 'Check your email' in driver.page_source
