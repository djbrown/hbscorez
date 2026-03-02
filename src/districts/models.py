from django.db import models
from django.urls import reverse

from associations.models import Association


class District(models.Model):
    name = models.TextField(unique=True)
    associations = models.ManyToManyField(Association)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("districts:detail", kwargs={"name": self.name})
