from django.db import models
from django.urls import reverse
from django.conf import settings
from django.templatetags.static import static

from model_utils.models import TimeStampedModel
from autoslug import AutoSlugField


class Speaker(TimeStampedModel):
    name = models.CharField('Nombre', max_length=255, unique=True)
    slug = AutoSlugField(
        null=True, default=None, unique=True, populate_from='name')
    description = models.TextField('Descripción', default='')
    image = models.ImageField(
        'Imagen', blank=True, null=True, upload_to='speakers')
    image_source_url = models.URLField(
        'Enlace a la fuente de la imagen', null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
    )
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='can_edit_speakers',
    )

    class Meta:
        verbose_name = 'Presentador'
        verbose_name_plural = 'Presentadores'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static('images/default_speaker_image.png')

    def get_absolute_url(self):
        return reverse('events:speaker_detail', args=[self.slug])

    def can_edit(self, user):
        if user.is_superuser or user == self.created_by or user in self.editors.all():
            return True
        return False
