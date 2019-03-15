from django.test import TestCase
from lxml import html

from base.parsing import parse_report_number


class ParseReportNumberTest(TestCase):

    def assert_from_markup(self, markup, expected):
        tree = html.fromstring(markup)
        actual = parse_report_number(tree)
        self.assertEqual(expected, actual)

    def test__empty_cell_markup__returns__none(self):
        markup = '<td></td>'
        expected = None
        self.assert_from_markup(markup, expected)

    def test__usual_markup__returns__correct_number(self):
        markup = '<td><a href="http://spo.handball4all.de/misc/sboPublicReports.php?sGID=123456"' \
                 ' target="_blank">PI</a>  </td>'
        expected = 123456
        self.assert_from_markup(markup, expected)

    def test__rescheduled_markup__returns__correct_number(self):
        markup = '<td><a href="http://spo.handball4all.de/misc/sboPublicReports.php?sGID=123456"' \
                 ' target="_blank">PI</a> <a style="cursor:help" title="geä. Anspielzeit">geä..</a></td>'
        expected = 123456
        self.assert_from_markup(markup, expected)
