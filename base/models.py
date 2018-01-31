from django.db import models
from django.urls import reverse


class Association(models.Model):
    name = models.TextField(unique=True)
    abbreviation = models.TextField()
    bhv_id = models.IntegerField(unique=True)

    def get_absolute_url(self):
        return reverse('association', kwargs={'pk': self.pk})

    def source_url(self):
        return 'https://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID={}'.format(self.bhv_id)

    def __str__(self):
        return 'Association: {}'.format(self.abbreviation)


class District(models.Model):
    name = models.TextField(unique=True)
    associations = models.ManyToManyField(Association)
    bhv_id = models.IntegerField(unique=True)

    def get_absolute_url(self):
        return reverse('district', kwargs={'pk': self.pk})

    def source_url(self):
        return 'https://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID={}&orgID={}'.format(
            self.associations.all()[0].bhv_id,
            self.bhv_id)

    def __str__(self):
        return 'District: {}'.format(self.name)


class League(models.Model):
    name = models.TextField()
    abbreviation = models.TextField()
    district = models.ForeignKey(District)
    bhv_id = models.IntegerField(unique=True)

    class Meta:
        unique_together = (('name', 'district'), ('abbreviation', 'district'))

    def get_absolute_url(self):
        return reverse('league', kwargs={'pk': self.pk})

    def players_url(self):
        return reverse('league_players', kwargs={'pk': self.pk})

    def bhv_url(self):
        return 'spo.handball4all.de/Spielbetrieb/index.php?orgGrpID={}&score={}'.format(
            self.district.associations.all()[0].bhv_id, self.bhv_id)

    def __str__(self):
        return 'League: {} ({})'.format(self.name, self.abbreviation)


class Team(models.Model):
    name = models.TextField()
    short_name = models.TextField()
    league = models.ForeignKey(League)
    bhv_id = models.IntegerField(unique=True)

    # logo = models.ImageField(upload_to=os.path.join(settings.MEDIA_ROOT, 'club-logos'))

    class Meta:
        unique_together = (('name', 'league'), ('short_name', 'league'))

    def get_absolute_url(self):
        return reverse('team', kwargs={'pk': self.pk, })

    def bhv_url(self):
        return 'https://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID={}&score={}&teamID={}'.format(
            self.league.district.associations.all()[0].bhv_id, self.league.bhv_id, self.bhv_id)

    def __str__(self):
        return 'Team: {}/{}'.format(self.name, self.league.abbreviation)


class Player(models.Model):
    name = models.TextField()
    team = models.ForeignKey(Team)

    def get_absolute_url(self):
        return reverse('player', kwargs={'pk': self.pk})

    def __str__(self):
        return 'Player: {}'.format(self.name)


class Game(models.Model):
    number = models.IntegerField(unique=True)
    league = models.ForeignKey(League)
    home_team = models.ForeignKey(Team, related_name='home_team')
    guest_team = models.ForeignKey(Team, related_name='guest_team')
    bhv_id = models.IntegerField(unique=True)

    def report_url(self):
        return 'https://spo.handball4all.de/misc/sboPublicReports.php?sGID={}'.format(self.bhv_id)

    class Meta:
        unique_together = ('home_team', 'guest_team')


class Score(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    goals = models.PositiveIntegerField(default=0)
    penalty_goals = models.PositiveIntegerField(default=0)
