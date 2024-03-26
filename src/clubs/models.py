from django.conf import settings
from django.db import models
from django.urls import reverse

from associations.models import Association


class Club(models.Model):
    name = models.TextField(unique=True)
    associations = models.ManyToManyField(Association)
    bhv_id = models.IntegerField(unique=True)

    def __str__(self):
        return f'{self.bhv_id} {self.name}'

    def get_absolute_url(self):
        return reverse('clubs:detail', kwargs={'bhv_id': self.bhv_id, })

    @staticmethod
    def build_source_url(bhv_id):
        return f'{settings.ROOT_SOURCE_URL}Spielbetrieb/index.php?orgGrpID=1&club={bhv_id}'

    def source_url(self):
        return self.build_source_url(self.bhv_id)
