from enum import Enum

from django.db import models


class Value(Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"


class Env(models.Model):
    name = models.TextField(unique=True)
    value = models.TextField()

    def set_value(self, value: Value):
        self.value = value.value
        self.save()
