import uuid

from django.db import models
from django.conf import settings

from model_utils.models import TimeStampedModel


DATETIME_PRECISION_DAY = 'day'
DATETIME_PRECISION_CHOICES = (
    ('year', 'Año'),
    ('month', 'Mes'),
    (DATETIME_PRECISION_DAY, 'Día'),
    ('hour', 'Hora'),
    ('minute', 'Minuto'),
)


class HistoricalFigure(TimeStampedModel):
    token = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        verbose_name='Nombre corto',
        max_length=255,
        help_text='Por ejemplo, "Simón Bolívar"',
    )
    full_name = models.CharField(
        verbose_name='Nombre completo',
        max_length=500,
        help_text='Por ejemplo, "Simón José Antonio de la Santísima Trinidad Bolívar '
                  'de la Concepción y Ponte Palacios y Blanco"',
    )
    sources = models.TextField('Fuentes de la información', default='', blank=True)

    image = models.ImageField('Imagen', blank=True, null=True, upload_to='history/historical-figures')
    image_source_url = models.URLField('Enlace a la fuente de la imagen', null=True, blank=True)

    date_of_birth = models.DateTimeField(db_index=True)
    date_of_birth_precision = models.CharField(max_length=15, choices=DATETIME_PRECISION_CHOICES)

    date_of_death = models.DateTimeField(db_index=True, blank=True, null=True)
    date_of_death_precision = models.CharField(
        max_length=15,
        choices=DATETIME_PRECISION_CHOICES,
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        verbose_name='Creado por',
        related_name='created_historical_figures',
    )

    class Meta:
        verbose_name = 'Personaje histórico'
        verbose_name_plural = 'Personajes históricos'

    def __str__(self):
        return self.name


class Event(TimeStampedModel):
    token = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        verbose_name='Título',
        max_length=500,
    )
    description = models.TextField('Descripción', default='', blank=True)
    sources = models.TextField('Fuentes de la información', default='', blank=True)

    image = models.ImageField('Imagen', blank=True, null=True, upload_to='history/events')
    image_source_url = models.URLField('Enlace a la fuente de la imagen', null=True, blank=True)

    event_date = models.DateTimeField(
        'Fecha del evento',
        db_index=True,
        help_text='p. ej. 23/11/2019 16:40',
    )
    event_date_precision = models.CharField(max_length=15, choices=DATETIME_PRECISION_CHOICES)
    location_name = models.CharField(max_length=500, default='', blank=True)

    event_end_date = models.DateTimeField(
        'Fecha final del evento',
        null=True,
        blank=True,
        db_index=True,
        help_text='p. ej. 23/11/2019 18:00 (opcional)',
    )
    event_end_date_precision = models.CharField(
        max_length=15,
        choices=DATETIME_PRECISION_CHOICES,
        blank=True,
        null=True,
    )

    historical_figures = models.ManyToManyField(
        'history.HistoricalFigure',
        related_name='history_events',
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        verbose_name='Creado por',
        related_name='created_history_events',
    )

    class Meta:
        verbose_name = 'Evento histórico'
        verbose_name_plural = 'Eventos históricos'


class Post(TimeStampedModel):
    token = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    TYPE_QUOTE = 'quote'
    TYPES = (
        (TYPE_QUOTE, 'Cita'),
    )
    type = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        choices=TYPES,
        db_index=True,
    )

    text = models.TextField('Texto')
    location_name = models.CharField(max_length=500, default='', blank=True)
    sources = models.TextField('Fuentes de la información', default='', blank=True)

    image = models.ImageField('Imagen', blank=True, null=True, upload_to='history/posts')
    image_source_url = models.URLField('Enlace a la fuente de la imagen', null=True, blank=True)

    post_date = models.DateTimeField(
        'Fecha de publicación',
        null=True,
        blank=True,
        db_index=True,
        help_text='p. ej. 23/11/2019 18:00 (opcional)',
    )
    post_date_precision = models.CharField(max_length=15, choices=DATETIME_PRECISION_CHOICES, blank=True, null=True)

    historical_figure = models.ForeignKey(
        'history.HistoricalFigure',
        related_name='written_posts',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        verbose_name='Creado por',
        related_name='created_history_posts',
    )
