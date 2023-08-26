from pathlib import Path

from django.conf import settings
from django.test import TestCase

from base import parsing


def read_html(file_name):
    file: Path = settings.ROOT_DIR / 'src' / 'base' / 'tests' / 'unit' / file_name
    content = file.read_text()
    return parsing.html_dom(content)


class ParseAssociationTest(TestCase):
    def test_urls(self):
        dom = read_html('portal.html')

        actual = parsing.parse_association_urls(dom)

        expected = [
            'https://www.handball4all.de/home/portal/bhv',
            'https://www.handball4all.de/home/portal/hhv',
            'https://www.handball4all.de/home/portal/lux',
            'https://www.handball4all.de/home/portal/hhhvsh',
            'https://www.handball4all.de/home/portal/hbbw',
            'https://www.handball4all.de/home/portal/rps',
            'https://www.handball4all.de/home/portal/pfalz',
            'https://www.handball4all.de/home/portal/hvrh',
            'https://www.handball4all.de/home/portal/hvs',
            'https://www.handball4all.de/home/portal/hvsh',
            'https://www.handball4all.de/home/portal/shv',
            'https://www.handball4all.de/home/portal/vhv',
            'https://www.handball4all.de/home/portal/westfalen',
            'https://www.handball4all.de/home/portal/hvw',
        ]
        self.assertEqual(expected, actual)

    def test_abbreviation(self):
        url = 'https://www.handball4all.de/home/portal/bhv'

        actual = parsing.parse_association_abbreviation(url)

        expected = 'BHV'
        self.assertEqual(expected, actual)

    def test_name(self):
        dom = read_html('association.html')

        actual = parsing.parse_association_name(dom)

        expected = 'Badischer Handball-Verband'
        self.assertEqual(expected, actual)

    def test_bhv_id(self):
        dom = read_html('association.html')

        actual = parsing.parse_association_bhv_id(dom)

        expected = 35
        self.assertEqual(expected, actual)
