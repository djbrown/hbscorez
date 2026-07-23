import logging

from django.conf import settings
from django.db import models
from django.urls import reverse

from clubs.models import Club
from leagues.models import League


class Team(models.Model):
    name = models.TextField()
    short_name = models.TextField()
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, blank=True, null=True, on_delete=models.SET_NULL)
    bhv_id = models.IntegerField(unique=True)
    retirement = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = (("name", "league"), ("short_name", "league"))

    def __str__(self):
        return f"{self.pk} {self.bhv_id} {self.short_name}"

    def get_absolute_url(self):
        return reverse("teams:detail", kwargs={"pk": self.pk})

    @staticmethod
    def build_api_url(district_bhv_id, league_bhv_id, team_bhv_id):
        return (
            settings.ROOT_SOURCE_URL
            + f"/service/if_g_json.php?cmd=ps&og={district_bhv_id}&cl={league_bhv_id}&ct={team_bhv_id}&ca=1"
        )

    def api_url(self):
        return Team.build_api_url(self.league.district.bhv_id, self.league.bhv_id, self.bhv_id)

    @staticmethod
    def build_source_url(league_bhv_id, team_bhv_id):
        return (
            f"{settings.ROOT_SOURCE_URL}/Spielbetrieb/index.php?orgGrpID=1&score={league_bhv_id}&teamID={team_bhv_id}"
        )

    def source_url(self):
        return self.build_source_url(self.league.bhv_id, self.bhv_id)
