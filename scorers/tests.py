import django
from django.db.models import Sum, Count
from django.test import TestCase

django.setup()

from scorers.models import PlayerScore


class ScorersTestCase(TestCase):
    def test_filter_order_doesnt_matter(self):
        q1 = PlayerScore.objects \
            .values('player_name') \
            .annotate(total=Sum('goals')) \
            .filter(total__gt=0) \
            .annotate(scores=Count('player_name')) \
            .annotate(penalties=Sum('penalty_goals')) \
            .order_by('-total')

        q2 = PlayerScore.objects \
            .values('player_name') \
            .annotate(total=Sum('goals')) \
            .annotate(scores=Count('player_name')) \
            .annotate(penalties=Sum('penalty_goals')) \
            .filter(total__gt=0) \
            .order_by('-total')

        self.assertEqual(list(q1), list(q2))
