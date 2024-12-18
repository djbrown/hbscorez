from django.test import TestCase

from base import parsing


class ParseReportNumberTest(TestCase):

    def assert_from_markup(self, markup, expected):
        dom = parsing.html_dom(markup)
        actual = parsing.parse_report_number(dom)
        self.assertEqual(expected, actual)

    def test_empty(self):
        markup = "<td></td>"
        expected = None
        self.assert_from_markup(markup, expected)

    def test_number(self):
        markup = (
            "<td>"
            '<a href="https://spo.handball4all.de/misc/sboPublicReports.php?sGID=123456" target="_blank">PI</a>  '
            "</td>"
        )
        expected = 123456
        self.assert_from_markup(markup, expected)

    def test_rescheduled(self):
        markup = (
            "<td>"
            '<a href="https://spo.handball4all.de/misc/sboPublicReports.php?sGID=123456" target="_blank">PI</a> '
            '<a style="cursor:help" title="geä. Anspielzeit">geä..</a>'
            "</td>"
        )
        expected = 123456
        self.assert_from_markup(markup, expected)


class ParseGameRemarkTest(TestCase):
    def assert_from_markup(self, markup, expected):
        dom = parsing.html_dom(markup)
        actual = parsing.parse_game_remark(dom)
        self.assertEqual(expected, actual)

    def test_empty(self):
        markup = "<td></td>"
        expected = ""
        self.assert_from_markup(markup, expected)

    def test_report_only(self):
        markup = (
            "<td>"
            '<a href="https://spo.handball4all.de/misc/sboPublicReports.php?sGID=123456" target="_blank">PI</a>  '
            "</td>"
        )
        expected = ""
        self.assert_from_markup(markup, expected)

    def test_remark_only(self):
        markup = '<td><a style="cursor:help" title="(2:0), gg. Gast">(2:0..</a></td>'
        expected = "(2:0), gg. Gast"
        self.assert_from_markup(markup, expected)

    def test_report_and_remark(self):
        markup = (
            "<td>"
            '<a href="https://spo.handball4all.de/misc/sboPublicReports.php?sGID=123456" target="_blank">PI</a> '
            '<a style="cursor:help" title="geä. Anspielzeit">geä..</a>'
            "</td>"
        )
        expected = "geä. Anspielzeit"
        self.assert_from_markup(markup, expected)
