import factory
import factory.fuzzy

from desparchado.tests.helpers import random_past_date
from users.tests.factories import UserFactory

from ..models import DATETIME_PRECISION_CHOICES, Event, Group, HistoricalFigure, Post


class EventFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('sentence')
    sources = factory.Faker('text')
    description = factory.Faker('text')
    image = factory.django.ImageField()
    event_date = factory.LazyFunction(random_past_date)
    event_date_precision = factory.fuzzy.FuzzyChoice(
        dict(DATETIME_PRECISION_CHOICES).keys(),
    )
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Event


class HistoricalFigureFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('name')
    full_name = factory.Faker('name')
    sources = factory.Faker('text')
    image = factory.django.ImageField()
    image_source_url = factory.Faker('url')
    date_of_birth = factory.LazyFunction(random_past_date)
    date_of_birth_precision = factory.fuzzy.FuzzyChoice(
        dict(DATETIME_PRECISION_CHOICES).keys(),
    )
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = HistoricalFigure
        django_get_or_create = ('name',)


class PostFactory(factory.django.DjangoModelFactory):
    type = factory.fuzzy.FuzzyChoice(dict(Post.TYPES).keys())
    text = factory.Faker('text')
    location_name = factory.Faker('sentence')
    sources = factory.Faker('text')
    image = factory.django.ImageField()
    image_source_url = factory.Faker('url')
    post_date = factory.LazyFunction(random_past_date)
    post_date_precision = factory.fuzzy.FuzzyChoice(
        dict(DATETIME_PRECISION_CHOICES).keys(),
    )
    historical_figure = factory.SubFactory(HistoricalFigureFactory)
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Post


class GroupFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('sentence')
    description = factory.Faker('text')
    image = factory.django.ImageField()
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Group
