from django.core.management import BaseCommand
from django.db import transaction

from base import models, logic
from base.middleware import env


class Command(BaseCommand):

    def handle(self, *args, **options):
        env.UPDATING.set_value(models.Value.TRUE)
        self.move_player(387733, "Philip Noske", "Philipp Noske")
        self.move_player(387733, "Frieder Schwarb", "Frieder Schwab")
        self.move_player(387733, "Patrick Dederich", "Patrick Dederichs")
        sghh = [
            ("David Krypczyk", 1,),
            ("Jakob Steinhilper", 1,),
            ("Benjamin Boudgoust", 1, 2,),
            ("Stephan Keibl", 1, 6,),
            ("Yannick Beer", 1, 4,),
            ("Jascha Lehnkering", 11, 2),
            ("Daniel Debatin", 12,),
            ("Raphael Blum", 13,),
            ("Maximilian Strüwing", 19, 3, 4, 3),
            ("Matthias Junker", 14, 3, 2, 1),
            ("Michael Förster", 18, 5),
            ("Maximilian Vollmer", 11, 2),
            ("Daniel Badawi", 17, 1),
        ]
        hcn = [
            ("Julian Frauendorff", 2, 2),
            ("Artur Pietrucha", 5, 7),
            ("Georg Kern", 7, 3),
            ("Jochen Werling", 10, 2),
            ("Findan Krettek", 12),
            ("Paul Nonnenmacher", 17),
            ("Jonas Kraus", 18, 7, 3, 3),
            ("Marius Angrick", 19, 5),
            ("Felix Kracht", 23, 1),
            ("Janick Nölle", 27),
            ("Marco Langjahr", 32, 4),
            ("Kevin Langjahr", 34, 1),
            ("Timo Bäuerlein", 62, 2),
        ]
        self.add_scores(210116, sghh, hcn)
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

    @transaction.atomic
    def add_scores(self, game_number, home_data, guest_data):
        game_matches = models.Game.objects.filter(number=game_number)
        if not game_matches.exists():
            self.stdout.write("SKIPPING Game (not found): {}".format(game_number))
            return

        game = game_matches[0]
        if game.score_set.exists():
            self.stdout.write("SKIPPING Game (existing scores): {}".format(game))
            return

        self._add_scores(game, game.home_team, home_data)
        self._add_scores(game, game.guest_team, guest_data)

    def _add_scores(self, game, team, data):
        for score in data:
            logic.add_score(*(game, team) + score, log_fun=self.stdout.write)
