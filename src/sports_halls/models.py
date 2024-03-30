from django.conf import settings
from django.db import models


class SportsHall(models.Model):
    number = models.IntegerField(unique=True)
    name = models.TextField()
    address = models.TextField()
    phone_number = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(blank=True, null=True, max_digits=9, decimal_places=6)
    longitude = models.DecimalField(blank=True, null=True, max_digits=9, decimal_places=6)
    bhv_id = models.IntegerField(unique=True)

    def __str__(self):
        return f"{self.number} {self.name}"

    @staticmethod
    def build_source_url(bhv_id):
        return f"{settings.ROOT_SOURCE_URL}Spielbetrieb/index.php?orgGrpID=1&gymID={bhv_id}"

    def source_url(self):
        return self.build_source_url(self.bhv_id)
