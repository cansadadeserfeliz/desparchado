from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as geo_models
from django.utils.translation import ugettext_lazy as _


from model_utils.models import TimeStampedModel


class Place(TimeStampedModel):
    name = models.CharField(verbose_name=_('Name'), max_length=255, unique=True)
    image = models.ImageField(null=True, blank=True, upload_to='places')
    image_source_url = models.URLField(null=True, blank=True)
    description = models.TextField(default='')
    website_url = models.URLField(null=True, blank=True)
    location = geo_models.PointField(null=False)
    city = models.ForeignKey('places.City', verbose_name=_('City'))

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.name

    def get_longitude_str(self):
        return str(self.location.x)

    def get_latitude_str(self):
        return str(self.location.y)

    def get_image_url(self):
        if self.image:
            return self.image.url
        return 'https://images.unsplash.com/photo-1485834532228-4fcb1456f84f?dpr=1&auto=compress,format&fit=crop&w=400&h=250&q=80&cs=tinysrgb&crop='


class City(TimeStampedModel):
    name = models.CharField(verbose_name=_('Name'), max_length=255, unique=True)
    center_location = geo_models.PointField(null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')
