from django.conf import settings
from django.db import models
from django.urls import reverse

from leagues.models import League


class Team(models.Model):
    name = models.TextField()
    short_name = models.TextField()
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    bhv_id = models.IntegerField(unique=True)
    retirement = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = (('name', 'league'), ('short_name', 'league'))

    def __str__(self):
        return '{} {}'.format(self.bhv_id, self.short_name)

    def get_absolute_url(self):
        return reverse('teams:detail', kwargs={'bhv_id': self.bhv_id, })

    @staticmethod
    def build_source_url(league_bhv_id, team_bhv_id):
        return settings.ROOT_SOURCE_URL + 'Spielbetrieb/index.php?orgGrpID=1&score={}&teamID={}'.format(league_bhv_id,
                                                                                                        team_bhv_id)

    def source_url(self):
        return self.build_source_url(self.league.bhv_id, self.bhv_id)
