from django.conf import settings
from django.db import models
from django.urls import reverse


class Association(models.Model):
    bhv_id = models.IntegerField('ID', unique=True)
    name = models.CharField('Name', max_length=255, unique=True)
    abbreviation = models.CharField('Abkürzung', max_length=255)

    class Meta:
        verbose_name = 'Verband'
        verbose_name_plural = 'Verbände'

    def __str__(self):
        return f'{self.bhv_id} {self.abbreviation}'

    def get_absolute_url(self):
        return reverse('associations:detail', kwargs={'bhv_id': self.bhv_id})

    @staticmethod
    def build_api_url(bhv_id):
        return f'{settings.ROOT_SOURCE_URL}service/if_g_json.php?cmd=po&og={bhv_id}'

    def api_url(self):
        return self.build_api_url(self.bhv_id)
