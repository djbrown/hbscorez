import os
from django.conf import settings
from django.db import models


class Club(models.Model):
    name = models.TextField(unique=True)
    logo = models.ImageField(upload_to=os.path.join(settings.MEDIA_ROOT, 'club-logos'))

    def __str__(self):
        return 'Club: {}'.format(self.name)


class Player(models.Model):
    name = models.TextField()
    club = models.ForeignKey(Club)

    def __str__(self):
        return 'Player: {}'.format(self.name)

    def get_url(self):
        return self.club.logo.url


class Score(models.Model):
    player = models.ForeignKey(Player)
    goals = models.PositiveIntegerField(default=0)
    penalty_goals = models.PositiveIntegerField(default=0)
