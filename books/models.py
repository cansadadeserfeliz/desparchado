from django.db import models
from django.urls import reverse
from django.core.validators import RegexValidator

from model_utils.models import TimeStampedModel
from autoslug import AutoSlugField


class BookQuerySet(models.QuerySet):
    def published(self):
        return self.filter(
            is_published=True,
        )


class Book(TimeStampedModel):
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
        upload_to='books/book',
    )
    isbn = models.CharField(
        max_length=50,
        unique=True,
        validators=[RegexValidator('\d{13}')],
    )
    is_published = models.BooleanField(
        'Está publicado',
        default=True,
        help_text='Indica si el libro va a aparecer en la página',
    )
    description = models.TextField('Descripción')

    related_events = models.ManyToManyField(
        'events.Event',
        related_name='books',
        blank=True,
    )
    press_articles = models.ManyToManyField(
        'news.PressArticle',
        verbose_name='Artículos de prensa',
        related_name='books',
        blank=True,
    )

    objects = BookQuerySet().as_manager()

    @staticmethod
    def autocomplete_search_fields():
        return ('title__icontains',)

    def get_image_url(self):
        return self.image.url

    def get_absolute_url(self):
        return reverse('books:book_detail', args=[self.slug])

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Libro'
        verbose_name_plural = 'Libros'
