import datetime

from django.conf import settings
from django.core.exceptions import EmptyResultSet
from django.db import models
from django.urls import reverse

from associations.models import Association


class District(models.Model):
    name = models.TextField(unique=True)
    associations = models.ManyToManyField(Association)
    bhv_id = models.IntegerField(unique=True)

    def __str__(self):
        return f"{self.pk} {self.bhv_id} {self.name}"

    def get_absolute_url(self):
        return reverse("districts:detail", kwargs={"pk": self.pk})

    @staticmethod
    def build_api_url(
        association_bhv_id: int | None = None,
        district_bhv_id: int | None = None,
        season_bhv_id: int | None = None,
        date: datetime.date | None = None,
    ):
        association_filter = f"&og={association_bhv_id}" if association_bhv_id else ""
        date_filter = f"&do={date}" if date else ""
        season_filter = f"&p={season_bhv_id}" if season_bhv_id else ""
        district_filter = f"&o={district_bhv_id}" if district_bhv_id else ""
        filters = association_filter + district_filter + season_filter + date_filter
        return f"{settings.ROOT_SOURCE_URL}/service/if_g_json.php?cmd=po{filters}"

    def api_url(self, season_bhv_id: int | None = None, date: datetime.date | None = None):
        association = self.associations.first()
        if association is None:
            raise EmptyResultSet(f"district without association: {self}")
        return self.build_api_url(association.bhv_id, self.bhv_id, season_bhv_id, date)

    def source_url(self, season_bhv_id=None, date: datetime.date | None = None):
        association = self.associations.first()
        if association is None:
            raise EmptyResultSet(f"district without association: {self}")
        association_url = association.source_url
        season_suffix = f"&pId={season_bhv_id}" if season_bhv_id else ""
        date_suffix = f"&wId={date}" if date else ""
        return f"{association_url}?oId={self.bhv_id}{season_suffix}{date_suffix}"
