import random

import factory
from factory.fuzzy import BaseFuzzyAttribute

from django.contrib.gis.geos import Point

from users.tests.factories import UserFactory
from ..models import Place
from ..models import City


class FuzzyPoint(BaseFuzzyAttribute):
    def fuzz(self):
        return Point(random.uniform(-180.0, 180.0),
                     random.uniform(-90.0, 90.0))


class CityFactory(factory.django.DjangoModelFactory):
    center_location = FuzzyPoint()
    name = factory.Faker('city')

    class Meta:
        model = City
        django_get_or_create = ('name',)


class PlaceFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('company')
    description = factory.fuzzy.FuzzyText(length=100)
    city = factory.SubFactory(CityFactory)
    location = FuzzyPoint()
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Place
        django_get_or_create = ('name',)
