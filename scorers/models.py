from django.db import models

from leagues.models import League


class Team(models.Model):
    name = models.TextField()
    league = models.ForeignKey(League)

    # logo = models.ImageField(upload_to=os.path.join(settings.MEDIA_ROOT, 'club-logos'))

    class Meta:
        unique_together = ('name', 'league')

    def __str__(self):
        return 'Team: {}/{}'.format(self.name, self.league.abbreviation)


class Player(models.Model):
    name = models.TextField()
    team = models.ForeignKey(Team)

    def __str__(self):
        return 'Player: {}'.format(self.name)

    def get_url(self):
        return self.team.logo.url


class Score(models.Model):
    player = models.ForeignKey(Player)
    goals = models.PositiveIntegerField(default=0)
    penalty_goals = models.PositiveIntegerField(default=0)
