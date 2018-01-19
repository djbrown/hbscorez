import django
from django.db.models import Sum, Count
from django.test import TestCase

django.setup()

from scorers.models import Score

