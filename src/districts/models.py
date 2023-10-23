import datetime

from django.conf import settings
from django.db import models
from django.urls import reverse

from associations.models import Association


class District(models.Model):
    bhv_id = models.IntegerField(verbose_name='ID', unique=True)
    name = models.CharField('Name', max_length=255, unique=True)
    associations = models.ManyToManyField(Association, verbose_name='Verbände')

    class Meta:
        verbose_name = 'Bezirk'
        verbose_name_plural = 'Bezirke'
        ordering = ('bhv_id',)

    def __str__(self):
        return f'{self.bhv_id} {self.name}'

    def get_absolute_url(self):
        return reverse('districts:detail', kwargs={'bhv_id': self.bhv_id})

    @staticmethod
    def build_source_url(bhv_id, date: datetime.date | None = None):
        date_suffix = f'&do={date}' if date else ''
        return f'{settings.ROOT_SOURCE_URL}Spielbetrieb/index.php?orgGrpID=1&orgID={bhv_id}{date_suffix}'

    def source_url(self, date: datetime.date | None = None):
        return self.build_source_url(self.bhv_id, date)
