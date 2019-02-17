from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.html import format_html
from django.templatetags.static import static

from model_utils.models import TimeStampedModel
from autoslug import AutoSlugField


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(
            is_published=True,
            is_approved=True,
        )


class Post(TimeStampedModel):
    title = models.CharField(
        'Título',
        max_length=255,
    )
    subtitle = models.CharField(
        'Título secundario',
        default='',
        max_length=255,
    )
    slug = AutoSlugField(
        null=False,
        unique=True,
        populate_from='title',
    )
    header_image = models.ImageField(
        'Imagen',
        blank=True,
        null=True,
        upload_to='posts'
    )
    content = models.TextField(
        verbose_name='Contenido',
        default='',
        help_text=format_html(
            'Puedes usar <a href="{}" target="_blank">Markdown</a> '
            'para dar formato al texto.',
            '/markdown',
        ),
    )

    is_published = models.BooleanField(
        'Está publicado',
        default=True,
        help_text='Indica si la entrada va a aparecer en la página',
    )
    is_approved = models.BooleanField(
        'Está aprobado', default=True,
        help_text='Campo de uso exclusivo para el administrador del sitio',
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Creado por',
        related_name='created_posts',
        on_delete=models.DO_NOTHING,
    )

    related_events = models.ManyToManyField(
        'events.Event',
        related_name='posts',
        blank=True,
    )

    objects = PostQuerySet().as_manager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.slug])

    def get_image_url(self):
        if self.header_image:
            return self.header_image.url
        return static('images/default_event_image.png')

