import factory
import factory.fuzzy

from desparchado.tests.helpers import random_future_date
from places.tests.factories import PlaceFactory
from users.tests.factories import UserFactory

from ..models import Event, Organizer, Speaker


class SpeakerFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('name')
    description = factory.Faker('text')
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Speaker
        django_get_or_create = ("name",)


class OrganizerFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('company')
    description = factory.Faker('text')
    website_url = 'https://example.com'
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Organizer
        django_get_or_create = ('name',)


class EventFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('sentence')
    event_date = factory.LazyFunction(random_future_date)
    category = factory.fuzzy.FuzzyChoice(dict(Event.Category.choices).keys())
    description = factory.Faker('text')
    image = factory.django.ImageField()
    price = factory.fuzzy.FuzzyDecimal(0, high=500_000, precision=2)
    event_source_url = factory.Faker('url')
    place = factory.SubFactory(PlaceFactory)
    created_by = factory.SubFactory(UserFactory)
    is_featured_on_homepage = True
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

    @factory.post_generation
    def speakers(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for speaker in extracted:
                self.speakers.add(speaker)

    class Meta:
        model = Event
