import logging
from collections import Counter

from django.conf import settings
from django.db import models
from django.urls import reverse
from fuzzywuzzy import process

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
        team = Team.objects.filter(bhv_id=bhv_id).first()
        if team is None:
            team = Team.objects.create(name=name, short_name=short_name, league=league, bhv_id=bhv_id)
            logger.info('CREATED Team: %s', team)
            return

        updated = False

        if team.name != name:
            team.name = name
            updated = True

        if team.short_name != short_name:
            team.short_name = short_name
            updated = True

        if updated:
            team.save()
            logger.info('UPDATED Team: %s', team)
        else:
            logger.debug('UNCHANGED Team: %s', team)

    def source_url(self):
        return self.build_source_url(self.league.bhv_id, self.bhv_id)

    @staticmethod
    def find_matching_short_name(name: str, short_names: list[str]) -> str:
        counter = Counter(short_names)
        by_count: list[tuple[str, int]] = counter.most_common()
        max_count: int = by_count[0][1]
        most_commons: list[str] = []
        for short_name, count in by_count:
            if count < max_count:
                break
            most_commons.append(short_name)
        return process.extractOne(name, set(most_commons))[0]

    @staticmethod
    def check_retirements(retirements, league, logger: logging.Logger = logging.getLogger()):
        for team_name, retirement_date in retirements:
            try:
                team = Team.objects.get(league=league, name=team_name)
            except Team.DoesNotExist:
                logger.warning('RETIRING team not found: %s %s', team_name, league)
                continue
            if team.retirement != retirement_date:
                team.retirement = retirement_date
                logger.info('RETIRING team %s on %s', team, retirement_date)
                team.save()
