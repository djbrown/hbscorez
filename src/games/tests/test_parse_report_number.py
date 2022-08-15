from django.test import TestCase
from lxml import html

from base import parsing


class ParseReportNumberTest(TestCase):

    def assert_from_markup(self, markup, expected):
        dom = html.fromstring(markup)
        actual = parsing.parse_report_number(dom)
        self.assertEqual(expected, actual)

    def test__empty_cell_markup__returns__none(self):
        markup = '<td></td>'
        expected = None
        self.assert_from_markup(markup, expected)

    def test__usual_markup__returns__correct_number(self):
        markup = '<td><a href="https://spo.handball4all.de/misc/sboPublicReports.php?sGID=123456"' \
                 ' target="_blank">PI</a>  </td>'
        expected = 123456
        self.assert_from_markup(markup, expected)

    def test__rescheduled_markup__returns__correct_number(self):
        markup = '<td><a href="https://spo.handball4all.de/misc/sboPublicReports.php?sGID=123456"' \
                 ' target="_blank">PI</a> <a style="cursor:help" title="geä. Anspielzeit">geä..</a></td>'
        expected = 123456
        self.assert_from_markup(markup, expected)
