import datetime
from datetime import timedelta
from random import randint

import factory
import factory.fuzzy

from users.tests.factories import UserFactory
from places.tests.factories import PlaceFactory
from ..models import Event
from ..models import Organizer


def random_future_date():
    return datetime.datetime.now() + timedelta(days=randint(1, 400))


class OrganizerFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=100)
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
