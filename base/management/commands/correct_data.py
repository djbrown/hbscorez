from django.core.management import BaseCommand
from django.db import transaction

from base import models
from base.management.commands import import_scores
from base.middleware import env


class Command(BaseCommand):

    def handle(self, *args, **options):
        env.UPDATING.set_value(models.Value.TRUE)
        self.move_player(387733, "Philip Noske", "Philipp Noske")
        self.move_player(387733, "Frieder Schwarb", "Frieder Schwab")
        self.move_player(387733, "Patrick Dederich", "Patrick Dederichs")
        sghh = [
            ("1", "David Krypczyk", '', ''),
            ("4", "Jakob Steinhilper", '', ''),
            ("6", "Benjamin Boudgoust", '2', ''),
            ("7", "Stephan Keibl", '6', ''),
            ("8", "Yannick Beer", '4', ''),
            ("11", "Jascha Lehnkering", '2', ''),
            ("12", "Daniel Debatin", '', ''),
            ("13", "Raphael Blum", '', ''),
            ("19", "Maximilian Strüwing", '3', '4/3'),
            ("24", "Matthias Junker", '3', '2/1'),
            ("28", "Michael Förster", '5', ''),
            ("71", "Maximilian Vollmer", '2', ''),
            ("77", "Daniel Badawi", '1', ''),
            ("A", "Roland Hähnel", '', ''),
            ("B", "Sandro Catak", '', ''),
            ("C", "Thomas Hinz", '', ''),
            ("D", "Daniel Philipp", '', ''),
        ]
        hcn = [
            ("2", "Julian Frauendorff", '2', ''),
            ("5", "Artur Pietrucha", '7', ''),
            ("7", "Georg Kern", '3', ''),
            ("10", "Jochen Werling", '2', ''),
            ("12", "Findan Krettek", '', ''),
            ("17", "Paul Nonnenmacher", '', ''),
            ("18", "Jonas Kraus", '7', '3/3'),
            ("19", "Marius Angrick", '5,', ''),
            ("23", "Felix Kracht", '1', ''),
            ("27", "Janick Nölle", '', ''),
            ("32", "Marco Langjahr", '4', ''),
            ("34", "Kevin Langjahr", '1', ''),
            ("62", "Timo Bäuerlein", '2', ''),
            ("A", "Achim Frautz", '', ''),
            ("C", "Janine Ensslin", '', ''),
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
            score = (score[0], score[1], None, None, None, score[2], score[3], None, None, None, None, None, None, None)
            import_scores.Command._add_score(self, game, team, score)
