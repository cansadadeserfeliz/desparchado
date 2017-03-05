from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as geo_models

from model_utils.models import TimeStampedModel


class Place(TimeStampedModel):
    name = models.CharField(max_length=255)
    image = models.ImageField(null=True)
    description = models.TextField()
    location = geo_models.PointField(null=False)
    city = models.ForeignKey('places.City')

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)


class City(TimeStampedModel):
    name = models.CharField(max_length=255)
    center_location = geo_models.PointField(null=False)


