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

        self.divide_player(391442, "Lisa Attinger", [11, 13])
        self.divide_player(385854, "Tim Baur", [5, 10])
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

    @transaction.atomic()
    def divide_player(self, team_bhv_id, original_name, numbers: list):
        self.stdout.write("DIVIDING Player: {} ({})".format(original_name, numbers))
        matches = models.Player.objects.filter(name=original_name, team__bhv_id=team_bhv_id)
        if matches.exists():
            original_player = matches[0]
            for score in original_player.score_set.all():
                if score.player_number not in numbers:
                    continue
                else:
                    new_name = "{} ({})".format(original_player.name, score.player_number)
                    new_player, created = models.Player.objects.get_or_create(name=new_name, team=original_player.team)
                    if created:
                        self.stdout.write("CREATED Player: {}".format(new_player))
                    score.player = new_player
                    score.save()
            self.stdout.write("DIVIDED Player: {} ({})".format(original_player, numbers))
            if not original_player.score_set.all().exists():
                self.stdout.write("DELETING Player (no dangling scores): {}".format(original_player))
                original_player.delete()
        else:
            self.stdout.write("SKIPPING Player (not found): {} ({})".format(original_name, team_bhv_id))
