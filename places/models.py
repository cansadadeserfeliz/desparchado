from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib.gis.db import models as geo_models
from django.templatetags.static import static

from autoslug import AutoSlugField
from model_utils.models import TimeStampedModel


class Place(TimeStampedModel):
    name = models.CharField('Nombre', max_length=255, unique=True)
    slug = AutoSlugField(
        null=True, default=None, unique=True, populate_from='name')
    image = models.ImageField(
        'Imagen', null=True, blank=True, upload_to='places')
    image_source_url = models.URLField(
        'Enlace a la fuente de la imagen', null=True, blank=True)
    description = models.TextField('Descripción', default='')
    website_url = models.URLField('Página web', null=True, blank=True)
    location = geo_models.PointField('Ubicación', null=False)
    city = models.ForeignKey('places.City', verbose_name='Ciudad')

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Creado por')

    class Meta:
        verbose_name = 'Lugar'
        verbose_name_plural = 'Lugares'

    def __str__(self):
        return self.name

    def get_longitude_str(self):
        return str(self.location.x)

    def get_latitude_str(self):
        return str(self.location.y)

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static('images/default_event_image.jpg')

    def get_absolute_url(self):
        return reverse('places:place_detail', args=[self.slug])

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains',)


class City(TimeStampedModel):
    name = models.CharField(verbose_name='Nombre', max_length=255, unique=True)
    center_location = geo_models.PointField(null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'
