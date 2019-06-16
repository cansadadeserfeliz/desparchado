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
    website_url = models.URLField('Página web', null=True, blank=True)
    description = models.TextField('Descripción', default='')

    def get_image_url(self):
        return self.image.url

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Media Source'
        verbose_name_plural = 'Media Sources'


class PressArticle(TimeStampedModel):
    title = models.CharField(
        'Título',
        max_length=255,
    )
    image = models.ImageField(
        'Background Image',
        blank=True,
        null=True,
        upload_to='news/press-article',
    )
    media_source = models.ForeignKey(
        'news.MediaSource',
        related_name='press_articles',
        on_delete=models.PROTECT,
    )
    source_url = models.URLField('Enlace a la página del artítulo')
    excerpt = models.TextField('Excerpt')

    def get_image_url(self):
        return self.image.url

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Press article'
        verbose_name_plural = 'Press articles'
