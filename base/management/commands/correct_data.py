from django.core.management import BaseCommand

from base import models
from base.middleware import env

bugged_reports = [567811, 562543]


class Command(BaseCommand):

    def handle(self, *args, **options):
        env.UPDATING.set_value(models.Value.TRUE)
        self.correct_games()
        self.correct_reports()
        self.correct_scores()
        env.UPDATING.set_value(models.Value.FALSE)

    def correct_games(self):
        pass

    def correct_reports(self):
        pass

    def correct_scores(self):
        pass

