from django.conf import settings
from django.db import models
from django.urls import reverse


class Association(models.Model):
    name = models.TextField(unique=True)
    abbreviation = models.TextField()
    bhv_id = models.IntegerField(unique=True)

    def __str__(self):
        return '{} {}'.format(self.bhv_id, self.abbreviation)

    def get_absolute_url(self):
        return reverse('associations:detail', kwargs={'bhv_id': self.bhv_id})

    @staticmethod
    def build_source_url(bhv_id):
        return settings.ROOT_SOURCE_URL + 'Spielbetrieb/index.php?orgGrpID={}'.format(bhv_id)

    def source_url(self):
        return self.build_source_url(self.bhv_id)

    @staticmethod
    def get_association_abbreviation(association_name):
        association_abbreviations = {
            'Badischer Handball-Verband': 'BHV',
            'Fédération Luxembourgeoise de Handball': 'FLH',
            'Hamburger Handball-Verband': 'HHV',
            'Handball Baden-Württemberg': 'HBW',
            'Handballoberliga Rheinland-Pfalz/Saar': 'RPS',
            'Handballverband Rheinhessen': 'HVR',
            'Handball-Verband Saar': 'HVS',
            'Handballverband Schleswig-Holstein': 'HVSH',
            'Handballverband Württemberg': 'HVW',
            'Mitteldeutscher Handball-Verband': 'MHV',
            'Oberliga Hamburg - Schleswig-Holstein': 'HHSH',
            'Südbadischer Handballverband': 'SHV',
            'Thüringer Handball-Verband': 'THV',
            'Vorarlberger Handballverband': 'VHV',
        }
        return association_abbreviations[association_name]
