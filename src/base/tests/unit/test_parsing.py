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
    def test_paths(self):
        dom = read_html("associations.html")

        actual = parsing.parse_association_paths(dom)

        expected = [
            "/verbaende/Baden",
            "/verbaende/Bayern",
            "/verbaende/Berlin",
            "/verbaende/Brandenburg",
            "/verbaende/Hamburg",
            "/verbaende/Hessen",
            "/verbaende/Mecklenburg-Vorpommern",
            "/verbaende/Niedersachsen",
            "/verbaende/Pfalz",
            "/verbaende/Rheinhessen",
            "/verbaende/Rheinland",
            "/verbaende/Saar",
            "/verbaende/Sachsen",
            "/verbaende/Sachsen-Anhalt",
            "/verbaende/Schleswig-Holstein",
            "/verbaende/Suedbaden",
            "/verbaende/Thueringer",
            "/verbaende/Westfalen",
            "/verbaende/Wuerttemberg",
            "/verbaende/Nordrhein",
            "/verbaende/Rheinhessen-Pfalz",
            "/verbaende/BWHV-Ligen",
            "/verbaende/DHB",
            "/verbaende/IHF",
            "/verbaende/EHF",
        ]
        self.assertEqual(expected, actual)

    def test_name(self):
        dom = read_html("association.html")

        actual = parsing.parse_association_name(dom)

        expected = "Badischer Handball-Verband"
        self.assertEqual(expected, actual)

    def test_short_name(self):
        url = "http://localhost/some/path/Association-ID"

        actual = parsing.parse_association_short_name(url)

        expected = "Association-ID"
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
