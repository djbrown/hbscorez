import json
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.test import TestCase

from base import parsing


def read_html(file_name):
    file: Path = settings.ROOT_DIR / "src" / "base" / "tests" / "unit" / file_name
    content = file.read_text()
    return parsing.html_dom(content)


class ParseAssociationTest(TestCase):
    def test_urls(self):
        dom = read_html("portal.html")

        actual = parsing.parse_association_urls(dom)

        expected = [
            "/home/portal/baden",
            "/home/portal/hamburg",
            "/home/portal/luxemburg",
            "/home/portal/oberliga-hh/hvsh",
            "/home/portal/oberliga-hbw",
            "/home/portal/oberliga-rps",
            "/home/portal/pfalz",
            "/home/portal/rheinhessen",
            "/home/portal/saarland",
            "/home/portal/schleswig-holstein",
            "/home/portal/suedbaden",
            "/home/portal/vorarlberg",
            "/home/portal/westfalen",
            "/home/portal/wuerttemberg",
        ]
        self.assertEqual(expected, actual)

    def test_abbreviation(self):
        file: Path = settings.ROOT_DIR / "src" / "base" / "tests" / "unit" / "association.json"
        json_text = file.read_text()

        actual = parsing.parse_association_abbreviation(json_text)

        expected = "PfHV"
        self.assertEqual(expected, actual)

    def test_name(self):
        dom = read_html("association.html")

        actual = parsing.parse_association_name(dom)

        expected = "Badischer Handball-Verband"
        self.assertEqual(expected, actual)

    def test_bhv_id(self):
        dom = read_html("association.html")

        actual = parsing.parse_association_bhv_id(dom)

        expected = 35
        self.assertEqual(expected, actual)


class ParseDistrictTest(TestCase):
    def test_parse_district_items(self):
        response = [
            {
                "menu": {
                    "org": {
                        "list": {
                            "4": "Handball Baden-Württemberg",
                            "35": "Badischer Handball-Verband",
                            "191": "Bezirk Rhein-Neckar-Tauber",
                            "196": "Bezirk Alb-Enz-Saal",
                            "84": "Bezirk Nord",
                            "43": "Bezirk Süd",
                            "36": "Bruchsal",
                            "37": "Heidelberg",
                            "38": "Karlsruhe",
                            "39": "Mannheim",
                            "40": "Pforzheim",
                            "82": "Neckar-Odenwald-Tauber",
                        },
                        "selectedID": "35",
                    }
                }
            }
        ]

        districts = parsing.parse_district_items(json.dumps(response, indent=0, ensure_ascii=True))

        self.assertTrue("4" in districts.keys())
        self.assertTrue("35" in districts.keys())
        self.assertTrue("191" in districts.keys())
        self.assertTrue("37" in districts.keys())

        self.assertTrue("Handball Baden-Württemberg" in districts.values())
        self.assertTrue("Badischer Handball-Verband" in districts.values())
        self.assertTrue("Bezirk Rhein-Neckar-Tauber" in districts.values())
        self.assertTrue("Heidelberg" in districts.values())

        self.assertTrue("Schriesheim" not in districts.values())


class ParseSportsHallTest(TestCase):
    def test_negative_longitude(self):
        dom = read_html("sport_hall_negative_longitude.html")

        actual = parsing.parse_sports_hall_coordinates(dom)

        expected = (Decimal("26.0377"), Decimal("-80.2951"))
        self.assertEqual(expected, actual)
