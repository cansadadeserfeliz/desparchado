from random import randint
from datetime import timedelta

from django.utils import timezone


def random_future_date():
    return timezone.now() + timedelta(days=randint(1, 400))
