from django.db import models
from django.urls import reverse


class Association(models.Model):
    name = models.TextField(unique=True)
    acronym = models.TextField()
    abbreviation = models.TextField(unique=True)

    def url(self):
        return reverse('association', kwargs={'id': self.id})

    def __str__(self):
        return 'Association: {}'.format(self.acronym)


class District(models.Model):
    name = models.TextField(unique=True)
    abbreviation = models.TextField(unique=True)
    association = models.ForeignKey(Association)

    def url(self):
        return reverse('district', kwargs={'id': self.id})

    def __str__(self):
        return 'District: {}'.format(self.abbreviation)


class League(models.Model):
    name = models.TextField()
    abbreviation = models.TextField()
    district = models.ForeignKey(District)

    class Meta:
        unique_together = (('name', 'district'), ('abbreviation', 'district'))

    def url(self):
        return reverse('league', kwargs={'id': self.id})

    def scorers_url(self):
        return reverse('league_scorers', kwargs={'id': self.id})

    def __str__(self):
        return 'League: {} - {}'.format(self.district.abbreviation, self.abbreviation)


class Team(models.Model):
    name = models.TextField()
    league = models.ForeignKey(League)

    # logo = models.ImageField(upload_to=os.path.join(settings.MEDIA_ROOT, 'club-logos'))

    class Meta:
        unique_together = ('name', 'league')

    def url(self):
        return reverse('team', kwargs={'id': self.id, })

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
