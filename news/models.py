from urllib.parse import urlparse
from urllib.parse import parse_qs

from django.db import models
from django.urls import reverse

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
    slug = AutoSlugField(
        null=False, unique=True,
        populate_from='title',
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
    content = models.TextField('Content', blank=True, null=True)

    def get_absolute_url(self):
        return reverse('news:press_article_detail', args=[self.slug])

    def get_image_url(self):
        return self.image.url

    def get_youtube_video_id(self):
        """
        Examples:
        - http://youtu.be/SA2iWivDJiE
        - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
        - http://www.youtube.com/embed/SA2iWivDJiE
        - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
        """
        if 'youtu' not in self.source_url:
            return None
        query = urlparse(self.source_url)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = parse_qs(query.query)
                return p['v'][0]
            if query.path[:7] == '/embed/':
                return query.path.split('/')[2]
            if query.path[:3] == '/v/':
                return query.path.split('/')[2]
        return None

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Press article'
        verbose_name_plural = 'Press articles'
        ordering = ('-publication_date',)
