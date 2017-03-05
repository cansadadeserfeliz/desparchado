from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as geo_models
from django.utils.translation import ugettext_lazy as _


from model_utils.models import TimeStampedModel


class Place(TimeStampedModel):
    name = models.CharField(verbose_name=_('Name'), max_length=255)
    image = models.ImageField(null=True, blank=True)
    description = models.TextField(default='')
    location = geo_models.PointField(null=False)
    city = models.ForeignKey('places.City', verbose_name=_('City'))

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.name


class City(TimeStampedModel):
    name = models.CharField(verbose_name=_('Name'), max_length=255)
    center_location = geo_models.PointField(null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')
