from django.test import TestCase

from leagues.models import League

YOUTH_LEAGUES = [
    ("wJE-KK-1", "männliche Jgd. E - Kreisklasse Staffel 1"),
    ("gJF", "gemischte Jugend F"),
    ("Minis", "Minispielfeste"),
    ("Mini-Mix", "Kreisliga Ostholstein Mini-Mix"),
    ("wMinis", "Minispielfeste weibliche Jugend"),
    ("wJC-RHL", "weibliche Jgd. C - Rheinhessenliga"),
    ("gJE-VRT-V", "gem. Jugend E VR-Talentiade Kreisvorentscheide"),
    ("rso-li-mjD", "RSO-Liga männl.D"),
]

NON_YOUTH_LEAGUES = [
    ("Inkl-SO", "Spielrunde Special Olympics"),
    ("M-RHL", "Männer Rheinhessenliga"),
    ("M-VL", "Männer Verbandsliga"),
    ("F-Pok-K", "Kreispokal Frauen"),
]


class Youth(TestCase):

    def test_youth(self):
        for abbreviation, name in YOUTH_LEAGUES:
            with self.subTest(abbreviation=abbreviation, name=name):
                self.assertTrue(League.is_youth(abbreviation=abbreviation, name=name))

    def test_non_youth(self):
        for abbreviation, name in NON_YOUTH_LEAGUES:
            with self.subTest(abbreviation=abbreviation, name=name):
                self.assertFalse(League.is_youth(abbreviation=abbreviation, name=name))
