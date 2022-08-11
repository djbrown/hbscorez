import logging

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
        return f'{self.bhv_id} {self.short_name}'

    def get_absolute_url(self):
        return reverse('teams:detail', kwargs={'bhv_id': self.bhv_id, })

    @staticmethod
    def build_source_url(league_bhv_id, team_bhv_id):
        return f'{settings.ROOT_SOURCE_URL}Spielbetrieb/index.php?orgGrpID=1&score={league_bhv_id}&teamID={team_bhv_id}'

    @staticmethod
    def create_or_update_team(name, short_name, league, bhv_id, logger: logging.Logger = logging.getLogger()):
        team = Team.objects.filter(league=league, bhv_id=bhv_id).first()
        if team:
            if team.name != name or team.short_name != short_name:
                team.name = name
                team.short_name = short_name
                team.save()
                logger.info('UPDATED Team: %s', team)
            else:
                logger.info('EXISTING Team: %s', team)
        else:
            team = Team.objects.create(name=name, short_name=short_name, league=league, bhv_id=bhv_id)
            logger.info('CREATED Team: %s', team)

    def source_url(self):
        return self.build_source_url(self.league.bhv_id, self.bhv_id)

    @staticmethod
    def find_matching_short_name(name: str, short_names: list[str]) -> str:
        return max(set(short_names), key=short_names.count)

