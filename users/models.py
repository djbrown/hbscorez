from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from players.models import Player


class Link(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    player = models.OneToOneField(Player, on_delete=models.CASCADE, unique=True)

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)
        if self.user.user_player_mapping_set.filter(team__league__season=self.player.team.league.season).exist():
            raise ValidationError('A User may only have one single Player Mapping per Season ')
