from django.conf import settings
from django.db import models


class SportsHall(models.Model):
    bhv_id = models.IntegerField(verbose_name='ID', unique=True)
    number = models.IntegerField(verbose_name='Hallennummer', unique=True)
    name = models.CharField(verbose_name='Name', max_length=255)
    address = models.CharField(verbose_name='Adresse', max_length=255)
    phone_number = models.CharField(verbose_name='Telefonnummer', max_length=255, blank=True, null=True)
    latitude = models.DecimalField(blank=True, null=True, max_digits=9, decimal_places=6)
    longitude = models.DecimalField(blank=True, null=True, max_digits=9, decimal_places=6)

    class Meta:
        verbose_name = 'Sporthalle'
        verbose_name_plural = 'Sporthallen'

    def __str__(self):
        return f"{self.number} {self.name}"

    @staticmethod
    def build_source_url(bhv_id):
        return f'{settings.ROOT_SOURCE_URL}Spielbetrieb/index.php?orgGrpID=1&gymID={bhv_id}'

    def source_url(self):
        return self.build_source_url(self.bhv_id)
