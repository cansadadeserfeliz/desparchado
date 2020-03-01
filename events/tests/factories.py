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
    title = factory.Faker('sentence')
    event_date = factory.LazyFunction(random_future_date)
    event_type = factory.fuzzy.FuzzyChoice(dict(Event.EVENT_TYPES).keys())
    description = factory.Faker('text')
    event_source_url = factory.Faker('url')
    topic = factory.fuzzy.FuzzyChoice(dict(Event.EVENT_TOPICS).keys())
    place = factory.SubFactory(PlaceFactory)
    created_by = factory.SubFactory(UserFactory)
    is_published = True
    is_approved = True

    @factory.post_generation
    def organizers(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for organizer in extracted:
                self.organizers.add(organizer)

    class Meta:
        model = Event
