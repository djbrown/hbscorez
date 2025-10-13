from django.conf import settings
from django.db import models
from django.urls import reverse


class Association(models.Model):
    name = models.TextField(unique=True)
    short_name = models.TextField(unique=True)
    source_url = models.TextField()
    abbreviation = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("associations:detail", kwargs={"short_name": self.short_name})


    def api_url(self):
        raise NotImplementedError("H4A API is offline")
