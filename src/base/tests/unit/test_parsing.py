from django.conf import settings
from django.test import TestCase

from base import parsing

from pathlib import Path
import json

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

        expected = 'bhv'
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
                            "82": "Neckar-Odenwald-Tauber"
                        },
                        "selectedID": "35"
                    }
                }
            }
        ]
        districts = parsing.parse_district_items(json.dumps(response, indent=0, ensure_ascii=True))
        
        self.assertTrue('4' in districts.keys())
        self.assertTrue('35' in districts.keys())
        self.assertTrue('191' in districts.keys())
        self.assertTrue('37' in districts.keys())

        self.assertTrue('Handball Baden-Württemberg' in districts.values())
        self.assertTrue('Badischer Handball-Verband' in districts.values())
        self.assertTrue('Bezirk Rhein-Neckar-Tauber' in districts.values())
        self.assertTrue('Heidelberg' in districts.values())

        self.assertTrue('Schriesheim' not in districts.values())

