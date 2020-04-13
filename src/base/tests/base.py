import os
import sys
import unittest
from contextlib import contextmanager

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command
from django.test import TestCase, tag
from django.urls import ResolverMatch, resolve, reverse
from sauceclient import SauceClient
from selenium.webdriver import Firefox, Remote
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support.ui import WebDriverWait

_CI = 'CI' in os.environ
_TUNNEL_ID = os.environ.get("TRAVIS_JOB_NUMBER")
_SAUCE_USER = os.environ.get("SAUCE_USERNAME")
_SAUCE_KEY = os.environ.get("SAUCE_ACCESS_KEY")


class ModelTestCase(TestCase):

    def assert_objects(self, model, count=1, filters=None):
        if filters is None:
            filters = {}

        objects = model.objects.filter(**filters)
        self.assertEqual(len(objects), count)
        return objects[0] if count == 1 else objects


@tag('integration', 'slow')
class IntegrationTestCase(ModelTestCase):

    def assert_command(self, command_name, *arguments, expected_return_code=None):
        return_code = call_command(command_name, *arguments)
        self.assertEqual(return_code, expected_return_code)


@unittest.skipUnless(settings.SELENIUM is True or _CI, 'Selenium test cases are only run in CI or if configured explicitly.')
@tag('selenium', 'slow')
class SeleniumTestCase(StaticLiveServerTestCase):

    def setUp(self):
        if _CI:
            self.driver = self.sauce_chrome_webdriver()
        elif settings.SELENIUM is True:
            options = FirefoxOptions()
            options.add_argument('-headless')
            self.driver = Firefox(firefox_options=options)
        self.driver.implicitly_wait(10)

    def sauce_chrome_webdriver(self):
        class_name = self.__class__.__name__
        method_name = self._testMethodName
        capabilities = {
            'platform': "Mac OS X 10.10",
            'browserName': "chrome",
            'version': "37.0",
            'name': '{}.{}'.format(class_name, method_name),
            'tunnel-identifier': _TUNNEL_ID,
        }

        executor = "http://{}:{}@ondemand.saucelabs.com/wd/hub".format(
            _SAUCE_USER,
            _SAUCE_KEY,
        )
        return Remote(
            command_executor=executor,
            desired_capabilities=capabilities,
        )

    def tearDown(self):
        self.driver.quit()
        if _CI:
            sauce_client = SauceClient(_SAUCE_USER, _SAUCE_KEY)
            status = (sys.exc_info() == (None, None, None))
            sauce_client.jobs.update_job(job_id=self.driver.session_id, build=_TUNNEL_ID,
                                         passed=status)

    def navigate(self, view_name: str, *args, **kwargs):
        path = reverse(view_name, args=args, kwargs=kwargs)
        self.driver.get(self.live_server_url + path)

    def assert_view(self, view_name: str):
        path: str = self.driver.current_url.replace(self.live_server_url, '')
        resolved: ResolverMatch = resolve(path)
        self.assertEqual(resolved.view_name, view_name)

    @contextmanager
    def load(self, timeout=1):
        page = self.driver.find_element_by_tag_name('html')
        yield
        WebDriverWait(self.driver, timeout).until(
            staleness_of(page)
        )

    @contextmanager
    def wait(self, timeout=settings.SELENIUM_TIMEOUT):
        condition = _UrlHasChanged(self.driver.current_url)
        yield
        WebDriverWait(self.driver, timeout).until(condition)


class _UrlHasChanged():

    def __init__(self, url):
        self.old_url = url

    def __call__(self, driver):
        return driver.current_url != self.old_url
