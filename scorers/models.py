from django.db import models


class District(models.Model):
    name = models.TextField(unique=True)
    abbreviation = models.TextField(unique=True)

    def __str__(self):
        return 'District: {}'.format(self.abbreviation)


class League(models.Model):
    name = models.TextField()
    abbreviation = models.TextField()
    district = models.ForeignKey(District)

    class Meta:
        unique_together = (('name', 'district'), ('abbreviation', 'district'))

    def __str__(self):
        return 'League: {} - {}'.format(self.district.abbreviation, self.abbreviation)


class Team(models.Model):
    name = models.TextField(unique=True)
    league = models.ForeignKey(League)

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
