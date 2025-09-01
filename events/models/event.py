
from autoslug import AutoSlugField
from django.conf import settings
from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

from desparchado.templatetags.desparchado_tags import format_currency


class EventQuerySet(models.QuerySet):
    def future(self):
        return self.filter(event_date__gte=timezone.now())

    def past(self):
        return self.filter(event_date__lt=timezone.now())

    def published(self):
        return self.filter(
            is_published=True,
            is_approved=True,
        ).select_related('place', 'place__city')


class Event(TimeStampedModel):

    title = models.CharField(
        'Título',
        max_length=255,
    )
    slug = AutoSlugField(
        null=False,
        unique=True,
        populate_from='title',
    )
    description = models.TextField(
        verbose_name='Descripción',
        default='',
    )

    class Category(models.TextChoices):
        LITERATURE = "literature", _("Literatura")
        SOCIETY = "society", _("Sociedad")
        ENVIRONMENT = "environment", _("Medio ambiente")
        SCIENCE = "science", _("Ciencia")
        ART = "art", _("Arte")

    category = models.CharField(
        verbose_name="Categoría",
        max_length=20,
        choices=Category,
        blank=True,
        db_index=True,
    )
    event_date = models.DateTimeField(
        'Fecha del evento',
        db_index=True,
        help_text='p. ej. 23/11/2019 16:40',
    )

    EVENT_SOURCE_URL_MAX_LENGTH = 500
    event_source_url = models.URLField(
        'Enlace a la página del evento',
        blank=False,
        max_length=EVENT_SOURCE_URL_MAX_LENGTH,
    )
    price = models.DecimalField('Precio', default=0, decimal_places=2, max_digits=9)
    image = models.ImageField('Imagen', blank=True, null=True, upload_to='events')
    image_source_url = models.URLField(
        'Créditos/atribución de la imagen',
        blank=True,
    )
    organizers = models.ManyToManyField(
        'events.Organizer',
        verbose_name='Organizadores',
        related_name='events',
        help_text='Por favor, asegúrate de que el/la organizador/a '
                  'que deseas asignar al evento no exista en nuestro sistema '
                  'antes de crearlo/a.',
    )
    place = models.ForeignKey(
        'places.Place',
        verbose_name='Lugar',
        related_name='events',
        on_delete=models.DO_NOTHING,
        db_index=True,
        help_text='Por favor, asegúrate de que el lugar '
                  'que deseas asignar al evento no exista en nuestro sistema '
                  'antes de crearlo.',
    )
    speakers = models.ManyToManyField(
        'events.Speaker',
        verbose_name='Presentadores',
        related_name='events',
        blank=True,
        help_text='Por favor, asegúrate de que el/la presentador/a '
                  'que deseas asignar al evento no exista en nuestro sistema '
                  'antes de crearlo/a.',
    )

    is_featured_on_homepage = models.BooleanField(
        'Está destacado en la página principal',
        default=False,
    )

    is_published = models.BooleanField(
        'Está publicado',
        default=True,
        help_text='Indica si el evento va a aparecer en la página',
    )
    is_approved = models.BooleanField(
        'Está aprobado',
        default=True,
        help_text='Campo de uso exclusivo para el administrador del sitio',
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        verbose_name='Creado por',
        related_name='created_events',
    )
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='can_edit_events',
    )

    filbo_id = models.CharField(
        verbose_name='ID del FILBo',
        max_length=10,
        null=True,
        blank=True,
        unique=True,
    )

    objects = EventQuerySet().as_manager()

    def __str__(self):
        return self.title

    def get_longitude_str(self):
        return self.place.get_longitude_str()

    def get_latitude_str(self):
        return self.place.get_latitude_str()

    def get_price_display(self):
        if self.price:
            return format_currency(self.price)
        return 'Gratuito'

    @property
    def image_url(self):
        return self.get_image_url()

    def get_image_url(self):
        if self.image:
            return self.image.url

        if self.filbo_id and self.event_date.year == 2025:
            return static('images/filbo-2025.jpg')
        return static('images/default_event_image.jpg')

    def get_absolute_url(self):
        return reverse('events:event_detail', args=[self.slug])

    def can_edit(self, user):
        if user.is_superuser or user == self.created_by or user in self.editors.all():
            return True
        return False

    @property
    def is_visible(self):
        return self.is_published and self.is_approved

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ('event_date',)
