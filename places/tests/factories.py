import random

import factory
from django.contrib.gis.geos import Point
from factory.fuzzy import BaseFuzzyAttribute

from users.tests.factories import UserFactory

from ..models import City, Place


class FuzzyPoint(BaseFuzzyAttribute):
    def fuzz(self):
        return Point(
            random.uniform(-74.4, -73.0),
            random.uniform(4.8, 4.66),
        )

class CityFactory(factory.django.DjangoModelFactory):
    center_location = FuzzyPoint()
    name = factory.Faker('city')
    description = factory.Faker('text')

    class Meta:
        model = City
        django_get_or_create = ('name',)


class PlaceFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('company')
    description = factory.Faker('text')
    city = factory.SubFactory(CityFactory)
    location = FuzzyPoint()
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Place
        django_get_or_create = ('name',)
