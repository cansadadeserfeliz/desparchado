import factory
import factory.fuzzy

from desparchado.tests.helpers import random_future_date
from users.tests.factories import UserFactory
from ..models import Event
from ..models import DATETIME_PRECISION_CHOICES


class EventFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('sentence')
    sources = factory.Faker('text')
    description = factory.Faker('text')
    image = factory.django.ImageField()
    event_date = factory.LazyFunction(random_future_date)
    event_date_precision = factory.fuzzy.FuzzyChoice(dict(DATETIME_PRECISION_CHOICES).keys())
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Event
