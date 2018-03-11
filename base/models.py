from django.db import models
from django.urls import reverse


class Association(models.Model):
    name = models.TextField(unique=True)
    abbreviation = models.TextField()
    bhv_id = models.IntegerField(unique=True)

    def __str__(self):
        return 'Association: {} {}'.format(self.bhv_id, self.abbreviation)

    def get_absolute_url(self):
        return reverse('association', kwargs={'bhv_id': self.bhv_id})

    def source_url(self):
        return 'https://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID={}'.format(self.bhv_id)


class District(models.Model):
    name = models.TextField(unique=True)
    associations = models.ManyToManyField(Association)
    bhv_id = models.IntegerField(unique=True)

    def __str__(self):
        return 'District: {} {}'.format(self.bhv_id, self.name)

    def get_absolute_url(self):
        return reverse('district', kwargs={'bhv_id': self.bhv_id})

    def source_url(self):
        return 'https://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID={}&orgID={}'.format(
            self.associations.all()[0].bhv_id,
            self.bhv_id)


class League(models.Model):
    name = models.TextField()
    abbreviation = models.TextField()
    district = models.ForeignKey(District)
    bhv_id = models.IntegerField(unique=True)

    class Meta:
        unique_together = (('name', 'district'), ('abbreviation', 'district'))

    def __str__(self):
        return 'League: {} {}'.format(self.bhv_id, self.name)

    def get_absolute_url(self):
        return reverse('league', kwargs={'bhv_id': self.bhv_id})

    def players_url(self):
        return reverse('league_players', kwargs={'bhv_id': self.bhv_id})

    def source_url(self):
        return 'https://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID={}&score={}&all=1'.format(
            self.district.associations.all()[0].bhv_id, self.bhv_id)



class Team(models.Model):
    name = models.TextField()
    short_name = models.TextField()
    league = models.ForeignKey(League)
    bhv_id = models.IntegerField(unique=True)
    # logo = models.ImageField(upload_to=os.path.join(settings.MEDIA_ROOT, 'club-logos'))

    class Meta:
        unique_together = (('name', 'league'), ('short_name', 'league'))

    def __str__(self):
        return '{} ({})'.format(self.short_name, self.bhv_id)

    def get_absolute_url(self):
        return reverse('team', kwargs={'bhv_id': self.bhv_id, })

    def source_url(self):
        return 'https://spo.handball4all.de/Spielbetrieb/index.php?orgGrpID={}&score={}&teamID={}'.format(
            self.league.district.associations.all()[0].bhv_id, self.league.bhv_id, self.bhv_id)


class Player(models.Model):
    name = models.TextField()
    team = models.ForeignKey(Team)

    def __str__(self):
        return '{} ({})'.format(self.name, self.team.short_name)

    def get_absolute_url(self):
        return reverse('player', kwargs={'pk': self.pk})



class Game(models.Model):
    number = models.IntegerField(unique=True)
    league = models.ForeignKey(League)
    opening_whistle = models.DateTimeField()
    home_team = models.ForeignKey(Team, related_name='home_team')
    guest_team = models.ForeignKey(Team, related_name='guest_team')
    home_goals = models.IntegerField(blank=True, null=True)
    guest_goals = models.IntegerField(blank=True, null=True)
    report_number = models.IntegerField(unique=True)
    def __str__(self):
        return '{} ({}): {} vs. {}'.format(self.number, self.league.abbreviation, self.home_team.short_name,
                                           self.guest_team.short_name)

    def report_url(self):
        return 'https://spo.handball4all.de/misc/sboPublicReports.php?sGID={}'.format(self.report_number)

    def opponent_of(self, team):
        if team == self.home_team:
            return self.guest_team
        elif team == self.guest_team:
            return self.home_team



class Score(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    goals = models.PositiveIntegerField(default=0)
    penalty_goals = models.PositiveIntegerField(default=0)
