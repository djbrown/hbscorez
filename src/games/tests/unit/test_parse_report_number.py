from django.test import TestCase

from base import parsing


class ParseReportNumberTest(TestCase):

    def assert_from_markup(self, markup, expected):
        dom = parsing.html_dom(markup)
        actual = parsing.parse_report_number(dom)
        self.assertEqual(expected, actual)

    def test_empty(self):
        markup = '<td></td>'
        expected = None
        self.assert_from_markup(markup, expected)

    def test_number(self):
        markup = '<td><a href="https://spo.handball4all.de/misc/sboPublicReports.php?sGID=123456"' \
                 ' target="_blank">PI</a>  </td>'
        expected = 123456
        self.assert_from_markup(markup, expected)

    def test_rescheduled(self):
        markup = '<td><a href="https://spo.handball4all.de/misc/sboPublicReports.php?sGID=123456"' \
                 ' target="_blank">PI</a> <a style="cursor:help" title="geä. Anspielzeit">geä..</a></td>'
        expected = 123456
        self.assert_from_markup(markup, expected)
