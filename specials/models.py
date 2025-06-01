from autoslug import AutoSlugField
from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel


class Special(TimeStampedModel):
    title = models.CharField(
        'Título',
        max_length=255,
    )
    subtitle = models.CharField(
        'Subtítulo',
        default='',
        max_length=500,
    )
    slug = AutoSlugField(
        null=False,
        unique=True,
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

    @property
    def events(self):
        return self.related_events.published().all()

    def get_absolute_url(self):
        return reverse('specials:special_detail', args=[self.slug])

    def get_image_url(self):
        return self.image.url

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Special'
        verbose_name_plural = 'Specials'
