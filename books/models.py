from django.db import models
from django.urls import reverse
from django.core.validators import RegexValidator
from django.templatetags.static import static

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
        db_index=True,
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
        validators=[RegexValidator(r'\d{13}')],
    )
    is_published = models.BooleanField(
        'Está publicado',
        default=True,
        help_text='Indica si el libro va a aparecer en la página',
    )
    description = models.TextField('Descripción')

    authors = models.ManyToManyField(
        'books.Author',
        related_name='books',
        blank=True,
    )

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
    blog_posts = models.ManyToManyField(
        'blog.Post',
        verbose_name='Entradas de blog',
        related_name='books',
        blank=True,
    )

    objects = BookQuerySet().as_manager()

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static('images/default_book_image.png')

    def get_absolute_url(self):
        return reverse('books:book_detail', args=[self.slug])

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Libro'
        verbose_name_plural = 'Libros'


class Author(TimeStampedModel):
    name = models.CharField(
        'Nombre completo',
        max_length=255,
        db_index=True,
    )
    slug = AutoSlugField(
        null=False, unique=True,
        populate_from='name',
    )
    speaker = models.OneToOneField(
        'events.Speaker',
        on_delete=models.PROTECT,
        related_name='book_author',
        blank=True,
        null=True,
    )

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains',)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Autor(a)'
        verbose_name_plural = 'Autores'
