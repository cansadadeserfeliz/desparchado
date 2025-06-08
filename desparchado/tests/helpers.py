from datetime import timedelta
from random import randint

from django.utils import timezone


def random_future_date():
    return timezone.now() + timedelta(days=randint(1, 400))


def random_past_date():
    return timezone.now() - timedelta(days=randint(1, 400))
