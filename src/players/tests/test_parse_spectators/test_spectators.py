import os

import tabula
from django.test import TestCase

from players.management.commands.parse_report import parse_spectators


class ParseSpectators(TestCase):

    def test_value(self):
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, 'report-with-spectators.pdf')
        table = tabula.read_pdf(path, output_format='json', **{'pages': 1, 'lattice': True})[0]

        spectators = parse_spectators(table)
        self.assertEqual(spectators, 60)

    def test_unknown(self):
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, 'report-with-unknown-spectators.pdf')
        table = tabula.read_pdf(path, output_format='json', **{'pages': 1, 'lattice': True})[0]

        spectators = parse_spectators(table)
        self.assertEqual(spectators, None)
