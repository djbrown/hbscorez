from django.core.management import BaseCommand

from associations.models import Association
from districts.models import District
from games.models import Game
from leagues.models import League
from players.models import Player, Score
from teams.models import Team


class Command(BaseCommand):
    def handle(self, *args, **options):
        Score.objects.all().delete()
        Game.objects.all().delete()
        Player.objects.all().delete()
        Team.objects.all().delete()
        League.objects.all().delete()
        District.objects.all().delete()
        Association.objects.all().delete()
