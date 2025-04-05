from django.db import models
from django.urls import reverse
from django.conf import settings
from django.templatetags.static import static

from model_utils.models import TimeStampedModel
from autoslug import AutoSlugField


class Organizer(TimeStampedModel):
    name = models.CharField('Nombre', max_length=255, unique=True)
    slug = AutoSlugField(
        null=False, unique=True, populate_from='name')
    description = models.TextField('Descripción', default='')
    website_url = models.URLField('Página web', null=True, blank=True)
    facebook_url = models.URLField('Página en Facebook', null=True, blank=True)
    twitter_url = models.URLField('Página en Twitter', null=True, blank=True)
    instagram_url = models.URLField('Página en Instagram', null=True, blank=True)
    image = models.ImageField(
        'Imagen', blank=True, null=True, upload_to='organizers')
    image_source_url = models.URLField(
        'Enlace a la fuente de la imagen', null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
    )
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='can_edit_organizers',
    )

    class Meta:
        verbose_name = 'Organizador'
        verbose_name_plural = 'Organizadores'

    def __str__(self):
        return self.name

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static('images/organizer-default.jpeg')

    def get_absolute_url(self):
        return reverse('events:organizer_detail', args=[self.slug])

    def can_edit(self, user):
        if user.is_superuser or user == self.created_by or user in self.editors.all():
            return True
        return False
