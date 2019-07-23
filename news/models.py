from django.db import models

from model_utils.models import TimeStampedModel
from autoslug import AutoSlugField


class MediaSource(TimeStampedModel):
    SOURCE_TYPE_BLOG = 'blog'
    SOURCE_TYPE_BOOKTUBE = 'booktube'
    SOURCE_TYPE_PODCAST = 'podcast'
    SOURCE_TYPE_MAGAZINE = 'magazine'
    SOURCE_TYPES = (
        (SOURCE_TYPE_BLOG, SOURCE_TYPE_BLOG),
        (SOURCE_TYPE_BOOKTUBE, SOURCE_TYPE_BOOKTUBE),
        (SOURCE_TYPE_PODCAST, SOURCE_TYPE_PODCAST),
        (SOURCE_TYPE_MAGAZINE, SOURCE_TYPE_MAGAZINE),
    )

    title = models.CharField(
        'Título',
        max_length=255,
    )
    source_type = models.CharField(
        'Tipo del recurso',
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
        choices=SOURCE_TYPES,
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
    publication_date = models.DateTimeField('Fecha de publicación')
    excerpt = models.TextField('Excerpt')

    @staticmethod
    def autocomplete_search_fields():
        return ('title__icontains',)

    def get_image_url(self):
        return self.image.url

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Press article'
        verbose_name_plural = 'Press articles'
        ordering = ('-publication_date',)
