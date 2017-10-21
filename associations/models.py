from django.db import models
from django.urls import reverse


class Association(models.Model):
    name = models.TextField(unique=True)
    acronym = models.TextField()
    abbreviation = models.TextField(unique=True)

    def get_absolute_url(self):
        params = {
            'assoc_abbr': self.abbreviation.lower(),
        }
        return reverse('assoc:index', kwargs=params)

    def __str__(self):
        return 'Association: {}'.format(self.acronym)
