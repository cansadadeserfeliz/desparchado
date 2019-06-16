from django.db import models

from model_utils.models import TimeStampedModel
from autoslug import AutoSlugField


class MediaSource(TimeStampedModel):
    title = models.CharField(
        'Título',
        max_length=255,
    )
    slug = AutoSlugField(
        null=False, unique=True,
        populate_from='title',
    )
    image = models.ImageField(
        'Background Image',
        blank=True,
        null=True,
        upload_to='news/media-source',
    )
    description = models.TextField('Descripción', default='')

    def get_image_url(self):
        return self.image.url
