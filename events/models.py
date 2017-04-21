from django.db import models
from django.urls import reverse
from django.conf import settings
from django.templatetags.static import static

from model_utils.models import TimeStampedModel
from autoslug import AutoSlugField

from desparchado.templatetags.desparchado_tags import format_currency


class EventPublishedManager(models.Manager):
    def get_queryset(self):
        return super(EventPublishedManager, self).get_queryset().filter(
            is_published=True,
            is_approved=True,
        )


class Event(TimeStampedModel):
    EVENT_TYPE_PUBLIC_LECTURE = 1
    EVENT_TYPE_DEBATE = 2
    EVENT_TYPE_MASTER_CLASS = 3
    EVENT_TYPE_TOUR = 4
    EVENT_TYPE_MEETING = 5
    EVENT_TYPE_THEATRICAL_PLAY = 6
    EVENT_TYPE_CONCERT = 7
    EVENT_TYPE_SEMINAR = 8

    EVENT_TYPES = (
        (EVENT_TYPE_PUBLIC_LECTURE, 'Conferencia pública'),
        (EVENT_TYPE_DEBATE, 'Debate'),
        (EVENT_TYPE_MASTER_CLASS, 'Taller'),
        (EVENT_TYPE_TOUR, 'Recorrido'),
        (EVENT_TYPE_MEETING, 'Encuentro'),
        (EVENT_TYPE_THEATRICAL_PLAY, 'Obra de teatro'),
        (EVENT_TYPE_CONCERT, 'Concierto'),
        (EVENT_TYPE_SEMINAR, 'Seminario'),
    )

    EVENT_TOPIC_CITY = 1
    EVENT_TOPIC_SCIENCE = 2
    EVENT_TOPIC_ART = 3
    EVENT_TOPIC_BUSINESS = 4
    EVENT_TOPIC_SOCIETY = 5
    EVENT_TOPIC_HUMAN_SCIENCE = 6
    EVENT_TOPIC_LANGUAGES = 7
    EVENT_TOPIC_LITERATURE = 8
    EVENT_TOPIC_ENVIRONMENT = 9
    EVENT_TOPIC_MEDICINE = 10
    EVENT_TOPICS = (
        (EVENT_TOPIC_CITY, 'Urbanismo'),
        (EVENT_TOPIC_SCIENCE, 'Ciencias exactas'),
        (EVENT_TOPIC_ART, 'Arte'),
        (EVENT_TOPIC_BUSINESS, 'Emprendimiento'),
        (EVENT_TOPIC_SOCIETY, 'Democracia'),
        (EVENT_TOPIC_HUMAN_SCIENCE, 'Ciencias humanas'),
        (EVENT_TOPIC_LANGUAGES, 'Idiomas'),
        (EVENT_TOPIC_LITERATURE, 'Literatura'),
        (EVENT_TOPIC_ENVIRONMENT, 'Medioambiente'),
        (EVENT_TOPIC_MEDICINE, 'Medicina'),
    )

    title = models.CharField(
        'Título', max_length=255,
        help_text='No hace falta usar mayúsculas: ya tenemos una fuente grande',
    )
    slug = AutoSlugField(
        null=False, unique=True, populate_from='title')

    description = models.TextField('Descripción', default='')
    event_type = models.PositiveSmallIntegerField(
        'Tipo del evento', choices=EVENT_TYPES)
    topic = models.PositiveSmallIntegerField('Tema', choices=EVENT_TOPICS)
    event_date = models.DateTimeField('Fecha del evento')
    event_end_date = models.DateTimeField('Fecha final', null=True, blank=True)
    event_source_url = models.URLField(
        'Enlace a la página del evento', null=True, blank=True)
    price = models.DecimalField(
        'Precio', default=0, decimal_places=2, max_digits=9)
    image = models.ImageField(
        'Imagen', blank=True, null=True, upload_to='events')
    image_source_url = models.URLField(
        'Créditos/atribución de la imagen', null=True, blank=True)
    organizer = models.ForeignKey(
        'events.Organizer', verbose_name='Organizador',
        related_name='events')
    place = models.ForeignKey(
        'places.Place', verbose_name='Lugar',
        related_name='events')
    speakers = models.ManyToManyField(
        'events.Speaker', verbose_name='Presentadores', blank=True, null=True)
    is_published = models.BooleanField('Está publicado', default=False)
    is_approved = models.BooleanField(
        'Está aprobado', default=True,
        help_text='Campo de uso exclusivo para el administrador del sitio',
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Creado por')

    published = EventPublishedManager()

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

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static('images/default_event_image.jpg')

    def get_absolute_url(self):
        return reverse('events:event_detail', args=[self.slug])

    @staticmethod
    def autocomplete_search_fields():
        return ('title__icontains',)

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ('event_date',)


class Organizer(TimeStampedModel):
    name = models.CharField('Nombre', max_length=255, unique=True)
    slug = AutoSlugField(
        null=False, unique=True, populate_from='name')
    description = models.TextField('Descripción', default='')
    website_url = models.URLField('Página web', null=True, blank=True)
    image = models.ImageField(
        'Imagen', blank=True, null=True, upload_to='organizers')
    image_source_url = models.URLField(
        'Enlace a la fuente de la imagen', null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        verbose_name = 'Organizador'
        verbose_name_plural = 'Organizadores'

    def __str__(self):
        return self.name

    def get_image_url(self):
        if self.image:
            return self.image.url
        return None

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains',)


class Speaker(TimeStampedModel):
    name = models.CharField('Nombre', max_length=255, unique=True)
    slug = AutoSlugField(
        null=True, default=None, unique=True, populate_from='name')
    description = models.TextField('Descripción', default='')
    image = models.ImageField(
        'Imagen', blank=True, null=True, upload_to='speakers')
    image_source_url = models.URLField(
        'Enlace a la fuente de la imagen', null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        verbose_name = 'Presentador'
        verbose_name_plural = 'Presentadores'

    def __str__(self):
        return self.name

    def get_image_url(self):
        if self.image:
            return self.image.url
        return None

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains',)
