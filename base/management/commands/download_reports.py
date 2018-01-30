from django.core.management import BaseCommand

from base.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        pass

    def download_report(self, game_number):
        pass

