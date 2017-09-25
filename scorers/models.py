from django.db import models


class PlayerScore(models.Model):
    player_name = models.TextField()
    goals = models.PositiveIntegerField(default=0)
    penalty_goals = models.PositiveIntegerField(default=0)
