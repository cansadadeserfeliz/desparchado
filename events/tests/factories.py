from datetime import timedelta
from random import randint

import factory
import factory.fuzzy

from django.utils import timezone

from users.tests.factories import UserFactory
from places.tests.factories import PlaceFactory
from ..models import Event
from ..models import Organizer
from ..models import Speaker


def random_future_date():
    return timezone.now() + timedelta(days=randint(1, 400))


class SpeakerFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('name')
    description = factory.fuzzy.FuzzyText(length=255)
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Speaker


class OrganizerFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('company')
    description = factory.fuzzy.FuzzyText(length=255)
    website_url = 'https://example.com'
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Organizer


class EventFactory(factory.django.DjangoModelFactory):
    title = factory.fuzzy.FuzzyText(length=100)
    event_date = factory.LazyFunction(random_future_date)
    event_type = factory.fuzzy.FuzzyChoice(dict(Event.EVENT_TYPES).keys())
    topic = factory.fuzzy.FuzzyChoice(dict(Event.EVENT_TOPICS).keys())
    organizer = factory.SubFactory(OrganizerFactory)
    place = factory.SubFactory(PlaceFactory)
    created_by = factory.SubFactory(UserFactory)
    is_published = True
    is_approved = True

    class Meta:
        model = Event
