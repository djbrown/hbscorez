from django.core.management import BaseCommand
from django.db import transaction

from base import models
from base.middleware import env


class Command(BaseCommand):

    def handle(self, *args, **options):
        env.UPDATING.set_value(models.Value.TRUE)
        self.move_player(387733, "Philip Noske", "Philipp Noske")
        self.move_player(387733, "Frieder Schwarb", "Frieder Schwab")
        self.move_player(387733, "Patrick Dederich", "Patrick Dederichs")
        env.UPDATING.set_value(models.Value.FALSE)

    @transaction.atomic
    def move_player(self, team_bhv_id, old_name, new_name):
        self.stdout.write("MOVING Player {} ({}) to {}".format(old_name, team_bhv_id, new_name))
        matches = models.Player.objects.filter(name=old_name, team__bhv_id=team_bhv_id)
        if matches.exists():
            old_player = matches[0]
            new_player, created = models.Player.objects.get_or_create(name=new_name, team=old_player.team)
            if old_player == new_player:
                self.stdout.write("SKIPPING Player (old equals new): {}".format(new_player))
            else:
                if created:
                    self.stdout.write("CREATED Player: {}".format(new_player))
                else:
                    self.stdout.write("EXISTING Player: {}".format(new_player))
                for score in old_player.score_set.all():
                    score.player = new_player
                    score.save()
                old_player.delete()
                self.stdout.write("CORRECTED Player: {} to {}".format(old_name, new_player))
        else:
            self.stdout.write("SKIPPING Player (not found): {} ({})".format(old_name, team_bhv_id))
