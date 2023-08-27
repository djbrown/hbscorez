from django.db import models
from django.urls import reverse


class Association(models.Model):
    name = models.TextField(unique=True)
    abbreviation = models.TextField()
    bhv_id = models.IntegerField(unique=True)
    source_url = models.TextField()

    def __str__(self):
        return f'{self.bhv_id} {self.abbreviation}'

    def get_absolute_url(self):
        return reverse('associations:detail', kwargs={'bhv_id': self.bhv_id})
