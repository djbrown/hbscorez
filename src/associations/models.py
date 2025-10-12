from django.conf import settings
from django.db import models
from django.urls import reverse


class Association(models.Model):
    name = models.TextField(unique=True)
    abbreviation = models.TextField()
    bhv_id = models.IntegerField(unique=True)
    source_url = models.TextField()

    def __str__(self):
        return f"{self.bhv_id} {self.abbreviation}"

    def get_absolute_url(self):
        return reverse("associations:detail", kwargs={"bhv_id": self.bhv_id})

    @staticmethod
    def build_api_url(bhv_id):
        return f"{settings.H4A_ROOT_SPO_URL}/service/if_g_json.php?cmd=po&og={bhv_id}"

    def api_url(self):
        return self.build_api_url(self.bhv_id)
