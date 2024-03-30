from pathlib import Path

import tabula
from django.test import TestCase

from players.management.commands.parse_report import parse_spectators


class ParseSpectators(TestCase):

    def test_value(self):
        path = Path(__file__).parent / "report-with-spectators.pdf"
        table = tabula.read_pdf(path, output_format="json", **{"pages": 1, "lattice": True})[0]

        spectators = parse_spectators(table)
        self.assertEqual(spectators, 60)

    def test_unknown(self):
        path = Path(__file__).parent / "report-with-unknown-spectators.pdf"
        table = tabula.read_pdf(path, output_format="json", **{"pages": 1, "lattice": True})[0]

        spectators = parse_spectators(table)
        self.assertEqual(spectators, None)

    def test_invalid(self):
        path = Path(__file__).parent / "report-with-invalid-spectators.pdf"
        table = tabula.read_pdf(path, output_format="json", **{"pages": 1, "lattice": True})[0]

        spectators = parse_spectators(table)
        self.assertEqual(spectators, None)
