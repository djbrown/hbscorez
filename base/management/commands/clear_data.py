from django.core.management import BaseCommand

from base.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        Score.objects.all().delete()
        Game.objects.all().delete()
        Player.objects.all().delete()
        Team.objects.all().delete()
        League.objects.all().delete()
        District.objects.all().delete()
        Association.objects.all().delete()
