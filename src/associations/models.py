from django.conf import settings
from django.db import models
from django.urls import reverse


class Association(models.Model):
    name = models.TextField(unique=True)
    abbreviation = models.TextField(blank=True, null=True)
    bhv_id = models.IntegerField(unique=True)
    source_url = models.TextField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("associations:detail", kwargs={"bhv_id": self.bhv_id})


    def api_url(self):
        raise NotImplementedError("H4A API offline")
