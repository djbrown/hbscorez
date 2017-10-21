from django.db import models
from django.urls import reverse

from districts.models import District


class League(models.Model):
    name = models.TextField()
    abbreviation = models.TextField()
    district = models.ForeignKey(District)

    class Meta:
        unique_together = (('name', 'district'), ('abbreviation', 'district'))

    def get_absolute_url(self):
        params = {
            'assoc_abbr': self.district.association.abbreviation.lower(),
            'dist_abbr': self.district.abbreviation.lower(),
            'league_abbr': self.abbreviation.lower(),
        }
        return reverse('assoc:dist:league:index', kwargs=params)

    def scorers_url(self):
        params = {
            'assoc_abbr': self.district.association.abbreviation.lower(),
            'dist_abbr': self.district.abbreviation.lower(),
            'league_abbr': self.abbreviation.lower(),
        }
        return reverse('assoc:dist:league:scorers', kwargs=params)

    def __str__(self):
        return 'League: {} - {}'.format(self.district.abbreviation, self.abbreviation)
