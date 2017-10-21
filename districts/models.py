from django.db import models
from django.urls import reverse

from associations.models import Association


class District(models.Model):
    name = models.TextField(unique=True)
    abbreviation = models.TextField(unique=True)
    association = models.ForeignKey(Association)

    def get_absolute_url(self):
        params = {
            'assoc_abbr': self.association.abbreviation.lower(),
            'dist_abbr': self.abbreviation.lower(),
        }
        return reverse('assoc:dist:index', kwargs=params)

    def __str__(self):
        return 'District: {}'.format(self.abbreviation)
