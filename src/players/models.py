from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from games.models import Game
from teams.models import Team


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    published = models.BooleanField(default=False)
    name = models.TextField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} {self.team.short_name}'

    def get_absolute_url(self):
        return reverse('players:detail', kwargs={'key': self.pk})

    def public_name(self):
        if self.user is not None and self.published is True \
                or settings.PUBLIC_NAMES is True:
            return self.name

        return 'Anonym'


class Score(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    player_number = models.IntegerField(blank=True, null=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    goals = models.IntegerField()
    penalty_goals = models.IntegerField()
    penalty_tries = models.IntegerField()
    warning_time = models.DurationField(blank=True, null=True)
    first_suspension_time = models.DurationField(blank=True, null=True)
    second_suspension_time = models.DurationField(blank=True, null=True)
    third_suspension_time = models.DurationField(blank=True, null=True)
    disqualification_time = models.DurationField(blank=True, null=True)
    report_time = models.DurationField(blank=True, null=True)
    team_suspension_time = models.DurationField(blank=True, null=True)

    class Meta:
        unique_together = ('player', 'game')

    def __str__(self):
        return f'{self.game.number} {self.player.name} ({self.player_number})'


class ReportsBlacklist(models.Model):
    report_number = models.IntegerField(unique=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.report_number}'
