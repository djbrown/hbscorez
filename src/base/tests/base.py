import os
import sys
from contextlib import contextmanager
from typing import Type

import pytest
from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command
from django.core.servers.basehttp import ThreadedWSGIServer
from django.db.models import Model
from django.db.models.query import QuerySet
from django.test import TestCase, tag
from django.test.runner import DiscoverRunner
from django.test.testcases import LiveServerThread, QuietWSGIRequestHandler
from django.urls import ResolverMatch, resolve, reverse
from sauceclient import SauceClient
from selenium.webdriver import Firefox, Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support.ui import WebDriverWait


class Runner(DiscoverRunner):

    def __init__(self, verbosity=1, failfast=False, keepdb=False, **kwargs):
        self.verbosity = verbosity
        self.failfast = failfast
        self.keepdb = keepdb
        super().__init__(**kwargs)

    def run_testss(self, test_labels, **kwargs):

        argv = []
        if self.verbosity == 0:
            argv.append('--quiet')
        if self.verbosity == 2:
            argv.append('--verbose')
        if self.verbosity == 3:
            argv.append('-vv')
        if self.failfast:
            argv.append('--exitfirst')
        if self.keepdb:
            argv.append('--reuse-db')

        argv.extend(test_labels)
        return pytest.main(argv)

    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        os.environ["DUMMY"] = "VALUE"
        suite = DiscoverRunner.build_suite(self, test_labels, extra_tests, **kwargs)
        return filter_tests_by_explicit_tags(suite, self.tags)


def filter_tests_by_explicit_tags(suite, cmd_tags):
    suite_class = type(suite)
    filtered_suite = suite_class()

    for test in suite:
        # recursion
        if isinstance(test, suite_class):
            filtered_suite.addTests(filter_tests_by_explicit_tags(test, cmd_tags))
            continue

        # gather class and function tags
        class_tags = set(getattr(test, 'explicit_tags', set()))
        func_name = getattr(test, '_testMethodName', str(test))
        func = getattr(test, func_name, test)
        func_tags = set(getattr(func, 'explicit_tags', set()))
        code_tags = class_tags.union(func_tags)

        if should_include_test(cmd_tags, code_tags):
            filtered_suite.addTest(test)

    return filtered_suite


def should_include_test(cmd_tags, code_tags) -> bool:
    return not code_tags if not cmd_tags else bool(code_tags.intersection(cmd_tags))


def skip_unless_any_tag(*tags):
    base_decorator = tag(*tags)

    def decorator(obj):
        obj = base_decorator(obj)
        if hasattr(obj, 'explicit_tags'):
            obj.tags = obj.tags.union(tags)
        else:
            setattr(obj, 'explicit_tags', set(tags))
        return obj
    return decorator


class ModelTestCase(TestCase):

    def assert_objects(self, model: Type[Model], count=1, filters=None) -> Model | QuerySet[Model]:
        if filters is None:
            filters = {}

        objects = model.objects.filter(**filters)
        self.assertEqual(len(objects), count)
        return objects[0] if count == 1 else objects


@pytest.mark.integration
@pytest.mark.slow
@skip_unless_any_tag('integration', 'slow')
class IntegrationTestCase(ModelTestCase):

    def assert_command(self, command_name, *arguments, expected_return_code=None):
        return_code = call_command(command_name, *arguments)
        self.assertEqual(return_code, expected_return_code)


class LiveServerThreadWithReuse(LiveServerThread):
    """
    This miniclass overrides _create_server to allow port reuse. This avoids creating
    "address already in use" errors for tests that have been run subsequently.
    """

    def _create_server(self, connections_override=None):
        return ThreadedWSGIServer(
            (self.host, self.port),
            QuietWSGIRequestHandler,
            allow_reuse_address=True,
            connections_override=connections_override,
        )


_CI = 'CI' in os.environ
_SAUCE_BUILD = os.environ.get("SAUCE_BUILD_NAME")
_SAUCE_TUNNEL = os.environ.get("SAUCE_TUNNEL_IDENTIFIER")
_SAUCE_USER = os.environ.get("SAUCE_USERNAME")
_SAUCE_KEY = os.environ.get("SAUCE_ACCESS_KEY")


@pytest.mark.selenium
@pytest.mark.slow
@skip_unless_any_tag('selenium', 'slow')
class SeleniumTestCase(StaticLiveServerTestCase):

    port = 8001
    server_thread_class = LiveServerThreadWithReuse

    """Selenium test cases are only run in CI or if configured explicitly"""

    def setUp(self):
        if _CI:
            self.driver = self.sauce_chrome_webdriver()
        else:
            options = FirefoxOptions()
            options.add_argument('-headless')
            self.driver = Firefox(options=options)
        self.driver.implicitly_wait(10)

    def sauce_chrome_webdriver(self):
        class_name = self.__class__.__name__
        method_name = self._testMethodName

        options = SafariOptions()
        options.browser_version = '14'
        options.platform_name = 'macOS 11.00'
        sauce_options = {
            'name': f'{class_name}.{method_name}',
            'build': _SAUCE_BUILD,
            'tunnelIdentifier': _SAUCE_TUNNEL,
            'username': _SAUCE_USER,
            'accessKey': _SAUCE_KEY,
        }
        options.set_capability('sauce:options', sauce_options)

        remote_url = "https://ondemand.us-west-1.saucelabs.com:443/wd/hub"
        return Remote(command_executor=remote_url, options=options)

    def tearDown(self):
        self.driver.quit()
        if _CI:
            sauce_client = SauceClient(_SAUCE_USER, _SAUCE_KEY)
            status = (sys.exc_info() == (None, None, None))
            sauce_client.jobs.update_job(job_id=self.driver.session_id, build=_SAUCE_TUNNEL,
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
        page = self.driver.find_element(By.TAG_NAME, 'html')
        yield
        WebDriverWait(self.driver, timeout).until(staleness_of(page))

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
