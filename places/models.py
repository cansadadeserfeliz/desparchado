from autoslug import AutoSlugField
from django.conf import settings
from django.contrib.gis.db import models as geo_models
from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from model_utils.models import TimeStampedModel


class Place(TimeStampedModel):
    name = models.CharField(
        'Nombre',
        max_length=255,
        unique=True,
        db_index=True,
    )
    slug = AutoSlugField(null=True, default=None, unique=True, populate_from='name')
    image = models.ImageField('Imagen', null=True, blank=True, upload_to='places')
    image_source_url = models.URLField(
        'Enlace a la fuente de la imagen', blank=True
    )
    description = models.TextField('Dirección', default='')
    website_url = models.URLField('Página web', blank=True)
    location = geo_models.PointField('Ubicación', null=False)
    city = models.ForeignKey(
        'places.City',
        verbose_name='Ciudad',
        on_delete=models.DO_NOTHING,
        db_index=True,
        null=True,
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Creado por',
        on_delete=models.DO_NOTHING,
    )
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='can_edit_places',
    )

    class Meta:
        verbose_name = 'Lugar'
        verbose_name_plural = 'Lugares'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_longitude_str(self):
        return str(self.location.x)  # pylint: disable=no-member

    def get_latitude_str(self):
        return str(self.location.y)  # pylint: disable=no-member

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static('images/default_place_image.png')

    def get_absolute_url(self):
        return reverse('places:place_detail', args=[self.slug])

    def can_edit(self, user):
        if user.is_superuser or user == self.created_by or user in self.editors.all():
            return True
        return False


class City(TimeStampedModel):
    name = models.CharField(
        verbose_name='Nombre',
        max_length=255,
        unique=True,
        db_index=True,
    )
    slug = AutoSlugField(null=True, default=None, unique=True, populate_from='name')
    image = models.ImageField('Imagen', null=True, blank=True, upload_to='places')
    image_source_url = models.URLField(
        'Enlace a la fuente de la imagen',
        blank=True
    )
    description = models.TextField('Descripción', blank=True, default='')
    center_location = geo_models.PointField(null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'

    def get_absolute_url(self):
        return reverse('places:city_detail', args=[self.slug])

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static('images/default_place_image.png')
