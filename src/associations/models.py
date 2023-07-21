from django.conf import settings
from django.db import models
from django.urls import reverse


class Association(models.Model):
    name = models.TextField(unique=True)
    abbreviation = models.TextField()
    bhv_id = models.IntegerField(unique=True)

    def __str__(self):
        return f'{self.abbreviation} ({self.bhv_id})'

    def get_absolute_url(self):
        return reverse('associations:detail', kwargs={'bhv_id': self.bhv_id})

    @staticmethod
    def build_source_url(bhv_id):
        return f'{settings.ROOT_SOURCE_URL}Spielbetrieb/index.php?orgGrpID={bhv_id}'

    def source_url(self):
        return self.build_source_url(self.bhv_id)

    @staticmethod
    def get_association_abbreviation(association_name: str) -> str | None:
        association_abbreviations = {
            'Badischer Handball-Verband': 'BHV',
            'Fédération Luxembourgeoise de Handball': 'FLH',
            'Hamburger Handball-Verband': 'HHV',
            'Handball Baden-Württemberg': 'HBW',
            'Handball-Verband Saar': 'HVS',
            'Handballoberliga Rheinland-Pfalz/Saar': 'RPS',
            'Handballverband Rheinhessen': 'HVR',
            'Handballverband Schleswig-Holstein': 'HVSH',
            'Handballverband Westfalen': 'HVWF',
            'Handballverband Württemberg': 'HVW',
            'Oberliga Hamburg - Schleswig-Holstein': 'HHSH',
            'Pfälzer Handballverband': 'PfHV',
            'Südbadischer Handballverband': 'SHV',
            'Vorarlberger Handballverband': 'VHV',
            # 'Mitteldeutscher Handball-Verband': 'MHV',
            # 'Thüringer Handball-Verband': 'THV',
        }

        for key in association_abbreviations:
            if key in association_name:
                return association_abbreviations[key]
        #return association_abbreviations[association_name]
