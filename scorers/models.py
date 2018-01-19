from django.db import models
from django.urls import reverse

from leagues.models import League


class Team(models.Model):
    name = models.TextField()
    league = models.ForeignKey(League)

    # logo = models.ImageField(upload_to=os.path.join(settings.MEDIA_ROOT, 'club-logos'))

    class Meta:
        unique_together = ('name', 'league')

    def get_absolute_url(self):
        params = {
            'team_id': self.id,
        }
        return reverse('team', kwargs=params)

    def __str__(self):
        return 'Team: {}/{}'.format(self.name, self.league.abbreviation)


class Player(models.Model):
    name = models.TextField()
    team = models.ForeignKey(Team)

    def __str__(self):
        return 'Player: {}'.format(self.name)

    def get_url(self):
        return self.team.logo.url


class Game(models.Model):
    number = models.IntegerField(unique=True)
    home_team = models.ForeignKey(Team, related_name='home_team')
    guest_team = models.ForeignKey(Team, related_name='guest_team')

    class Meta:
        unique_together = ('home_team', 'guest_team')


class Score(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    goals = models.PositiveIntegerField(default=0)
    penalty_goals = models.PositiveIntegerField(default=0)
