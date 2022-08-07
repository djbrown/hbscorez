from django.conf import settings
from django.core import validators
from django.db import models
from django.urls import reverse

from districts.models import District


class Season(models.Model):
    start_year = models.PositiveIntegerField(unique=True, validators=[
        validators.MinValueValidator(1990),
        validators.MaxValueValidator(2050)])

    def __str__(self):
        return f'{self.start_year}/{self.start_year + 1}'


class League(models.Model):
    name = models.TextField()
    abbreviation = models.TextField()
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    bhv_id = models.IntegerField(unique=True)

    class Meta:
        unique_together = (('name', 'district', 'season'), ('abbreviation', 'district', 'season'))

    def __str__(self):
        return f'{self.bhv_id} {self.name} {self.season}'

    def get_absolute_url(self):
        return reverse('leagues:detail', kwargs={'bhv_id': self.bhv_id})

    @staticmethod
    def build_source_url(bhv_id):
        return f'{settings.ROOT_SOURCE_URL}Spielbetrieb/index.php?orgGrpID=1&all=1&score={bhv_id}'

    def source_url(self):
        return self.build_source_url(self.bhv_id)

    @property
    def youth(self) -> bool:
        return self.is_youth(self.abbreviation, self.name)

    @staticmethod
    def is_youth(abbreviation: str, name: str) -> bool:
        youth_name_indicators_direct = [
            'Jugend', 'Jgd', 'Mini', 'Jungen', 'Mädchen',
            'Jongen', 'Meedercher', 'weiblich', 'männlich',
            'Auswahl', 'Mini']
        youth_names_indicators_two_letters = [
            gender + age_class
            for gender in ['m', 'w']
            for age_class in ['A', 'B', 'C', 'D', 'E']]
        youth_names_indicators_three_letters = [
            gender + 'J' + age_class
            for gender in ['M', 'W', 'm', 'w']
            for age_class in ['A', 'B', 'C', 'D', 'E']]
        youth_match_strong = any(n in name for n in
                                 youth_name_indicators_direct
                                 + youth_names_indicators_two_letters
                                 + youth_names_indicators_three_letters)

        adult_name_indicators = [
            'Männer', 'Frauen', 'Herren', 'Damen',
            'Hären', 'Dammen', 'Senioren', 'Seniorinnen',
            'Hommes', 'Dames', 'Fraen',
            'Inklusion', 'Special Olympics']
        adult_match_strong = any(n in name for n in adult_name_indicators)

        if youth_match_strong != adult_match_strong:
            return youth_match_strong
        if youth_match_strong and adult_match_strong:
            raise YouthUndecidableError(abbreviation, name)

        youth_match_weak = abbreviation[:1] in ['m', 'w', 'g', 'u', 'U']
        adult_match_weak = abbreviation[:1] in ['M', 'F', 'Ü']
        if youth_match_weak != adult_match_weak:
            return youth_match_weak

        raise YouthUndecidableError(abbreviation, name)


class LeagueName(models.Model):
    bhv_id = models.IntegerField(unique=True)
    name = models.TextField()

    def __str__(self):
        return f'{self.bhv_id} {self.name}'


class YouthUndecidableError(Exception):
    def __init__(self, abbreviation: str, name: str) -> None:
        message = f"Youth undecidable: '{abbreviation}' '{name}'"
        super().__init__(message)
