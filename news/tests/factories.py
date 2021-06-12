import factory
import factory.fuzzy

from desparchado.tests.helpers import random_past_date
from ..models import MediaSource
from ..models import PressArticle


class MediaSourceFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('sentence')
    image = factory.django.ImageField()
    source_type = factory.fuzzy.FuzzyChoice(dict(MediaSource.SOURCE_TYPES).keys())
    description = factory.Faker('text')

    class Meta:
        model = MediaSource


class PressArticleFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('sentence')
    image = factory.django.ImageField()
    media_source = factory.SubFactory(MediaSourceFactory)
    source_url = factory.Faker('url')
    publication_date = factory.LazyFunction(random_past_date)
    excerpt = factory.Faker('text')

    class Meta:
        model = PressArticle
