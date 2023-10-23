from enum import Enum

from django.db import models


class Value(Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"


class Env(models.Model):
    name = models.CharField(unique=True, max_length=255)
    value = models.TextField()

    class Meta:
        verbose_name = 'Umgebungsvariable'
        verbose_name_plural = 'Umgebungsvariablen'

    def set_value(self, value: Value):
        self.value = value.value
        self.save()


class GlobalMessage(models.Model):
    message = models.TextField()

    def __str__(self):
        return self.message[:20]
