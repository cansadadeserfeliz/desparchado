from django.db import models
from django.urls import reverse

from model_utils.models import TimeStampedModel
from autoslug import AutoSlugField


class Special(TimeStampedModel):
    title = models.CharField(
        'Título',
        max_length=255,
    )
    slug = AutoSlugField(
        null=False, unique=True,
        populate_from='title',
    )
    is_published = models.BooleanField(
        'Está publicado',
        default=True,
    )
    image = models.ImageField(
        'Background Image',
        blank=True,
        null=True,
        upload_to='specials',
    )
    related_events = models.ManyToManyField(
        'events.Event',
        related_name='specials',
        blank=True,
    )
    description = models.TextField('Descripción', default='')

    def get_absolute_url(self):
        return reverse('specials:special_detail', args=[self.slug])
