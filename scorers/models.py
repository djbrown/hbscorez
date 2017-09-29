from django.db import models


class Club(models.Model):
    name = models.TextField(unique=True)
    logo = models.ImageField()

    def __str__(self):
        return 'Club: {}'.format(self.name)


class Score(models.Model):
    player_name = models.TextField()
    goals = models.PositiveIntegerField(default=0)
    penalty_goals = models.PositiveIntegerField(default=0)
    club = models.ForeignKey(Club)
