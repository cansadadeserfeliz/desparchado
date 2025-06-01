import uuid

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.template.defaultfilters import date as _date
from django.template.defaultfilters import time as _time
from django.templatetags.static import static
from django.urls import reverse
from model_utils.models import TimeStampedModel

DATETIME_PRECISION_DAY = 'day'
DATETIME_PRECISION_YEAR = 'year'
DATETIME_PRECISION_MONTH = 'month'
DATETIME_PRECISION_HOUR = 'hour'
DATETIME_PRECISION_MINUTE = 'minute'
DATETIME_PRECISION_CHOICES = (
    (DATETIME_PRECISION_YEAR, 'Año'),
    (DATETIME_PRECISION_MONTH, 'Mes'),
    (DATETIME_PRECISION_DAY, 'Día'),
    (DATETIME_PRECISION_HOUR, 'Hora'),
    (DATETIME_PRECISION_MINUTE, 'Minuto'),
)


def get_historical_date_display(historical_date, precision):
    """
    Formats a given date according to precision.

    :param historical_date: (datetime) historical date to format
    :param precision: (str) precision from DATETIME_PRECISION_CHOICES
    :return: (str) formatted date
    """
    date_str = _date(historical_date, 'Y')
    if precision != DATETIME_PRECISION_YEAR:
        date_str = _date(historical_date, 'F').lower() + ' ' + date_str
    if precision != DATETIME_PRECISION_YEAR and precision != DATETIME_PRECISION_MONTH:
        date_str = _date(historical_date, 'j') + ' de ' + date_str
    if precision == DATETIME_PRECISION_HOUR:
        date_str = date_str + ', ' + _time(historical_date, 'g a')
    if precision == DATETIME_PRECISION_MINUTE:
        date_str = date_str + ', ' + _time(historical_date, 'g:i a')

    return date_str


class HistoricalFigure(TimeStampedModel):
    token = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        verbose_name='Nombre corto',
        max_length=255,
        db_index=True,
        help_text='Por ejemplo, "Simón Bolívar"',
    )
    full_name = models.CharField(
        verbose_name='Nombre completo',
        max_length=500,
        default='',
        blank=True,
        help_text='Por ejemplo, "Simón José Antonio de la Santísima Trinidad Bolívar '
        'de la Concepción y Ponte Palacios y Blanco"',
    )
    description = models.TextField('Descripción', default='', blank=True)
    labels = ArrayField(models.CharField(max_length=15), blank=True, default=list)
    sources = models.TextField('Fuentes de la información', default='', blank=True)
    admin_comments = models.TextField(
        'Comentarios de los administradores', default='', blank=True
    )

    image = models.ImageField(
        'Imagen', blank=True, null=True, upload_to='history/historical-figures'
    )
    image_source_url = models.URLField(
        'Enlace a la fuente de la imagen', null=True, blank=True
    )

    date_of_birth = models.DateTimeField(db_index=True)
    date_of_birth_precision = models.CharField(
        max_length=15,
        default=DATETIME_PRECISION_DAY,
        choices=DATETIME_PRECISION_CHOICES,
    )

    date_of_death = models.DateTimeField(db_index=True, blank=True, null=True)
    date_of_death_precision = models.CharField(
        max_length=15,
        default=DATETIME_PRECISION_DAY,
        choices=DATETIME_PRECISION_CHOICES,
        blank=True,
        null=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        verbose_name='Creado por',
        related_name='created_historical_figures',
    )

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static('images/default_historical_figure_image.jpg')

    def get_absolute_url(self):
        return reverse('history:historical_figure_detail', args=[self.token])

    def get_date_of_birth_display(self):
        return get_historical_date_display(
            self.date_of_birth, self.date_of_birth_precision
        )

    def get_date_of_death_display(self):
        if self.date_of_death:
            return get_historical_date_display(
                self.date_of_death, self.date_of_death_precision
            )
        return '-'

    class Meta:
        ordering = ['name']
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
    admin_comments = models.TextField(
        'Comentarios de los administradores', default='', blank=True
    )

    image = models.ImageField(
        'Imagen', blank=True, null=True, upload_to='history/events'
    )
    image_source_url = models.URLField(
        'Enlace a la fuente de la imagen', null=True, blank=True
    )

    event_date = models.DateTimeField(
        'Fecha del evento',
        db_index=True,
        help_text='p. ej. 23/11/2019 16:40',
    )
    event_date_precision = models.CharField(
        max_length=15,
        default=DATETIME_PRECISION_DAY,
        choices=DATETIME_PRECISION_CHOICES,
    )
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
        default=DATETIME_PRECISION_DAY,
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

    def get_event_date_display(self):
        return get_historical_date_display(self.event_date, self.event_date_precision)

    def get_event_day_and_month_display(self):
        if self.event_date_precision == DATETIME_PRECISION_YEAR:
            return '-'
        if self.event_date_precision == DATETIME_PRECISION_MONTH:
            return _date(self.event_date, 'b')
        return _date(self.event_date, 'j b')

    def get_event_end_date_display(self):
        if self.event_end_date:
            return get_historical_date_display(
                self.event_end_date, self.event_end_date_precision
            )
        return '-'

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-event_date']
        verbose_name = 'Evento histórico'
        verbose_name_plural = 'Eventos históricos'

    def get_absolute_url(self):
        return reverse('history:event_detail', kwargs={'token': self.token})


class Post(TimeStampedModel):
    token = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    TYPE_QUOTE = 'quote'
    TYPE_TRAVEL = 'Travel'
    TYPE_MARRIAGE = 'marriage'
    TYPE_LOSS = 'loss'
    TYPES = (
        (TYPE_QUOTE, 'Cita'),
        (TYPE_TRAVEL, 'Viaje'),
        (TYPE_MARRIAGE, 'Matrimonio'),
        (TYPE_LOSS, 'Pérdida de un ser querido'),
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
    admin_comments = models.TextField(
        'Comentarios de los administradores', default='', blank=True
    )

    image = models.ImageField(
        'Imagen', blank=True, null=True, upload_to='history/posts'
    )
    image_source_url = models.URLField(
        'Enlace a la fuente de la imagen', null=True, blank=True
    )

    post_date = models.DateTimeField(
        'Fecha de publicación',
        null=True,
        blank=True,
        db_index=True,
        help_text='p. ej. 23/11/2019 18:00 (opcional)',
    )
    post_date_precision = models.CharField(
        max_length=15,
        default=DATETIME_PRECISION_DAY,
        choices=DATETIME_PRECISION_CHOICES,
        blank=True,
        null=True,
    )

    historical_figure = models.ForeignKey(
        'history.HistoricalFigure',
        related_name='written_posts',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    historical_figure_mentions = models.ManyToManyField(
        'history.HistoricalFigure',
        related_name='mentioned_in_posts',
        blank=True,
    )
    published_in_groups = models.ManyToManyField(
        'history.Group',
        related_name='posts',
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        verbose_name='Creado por',
        related_name='created_history_posts',
    )

    class Meta:
        ordering = ['-post_date']

    def get_post_type_subtitle(self):
        if self.type == self.TYPE_TRAVEL:
            return 'está viajando'
        if self.type == self.TYPE_MARRIAGE:
            return 'se casó'
        if self.type == self.TYPE_LOSS:
            return 'perdió a un ser querido'
        return ''

    def get_post_type_icon_class(self):
        if self.type == self.TYPE_TRAVEL:
            return 'fas fa-suitcase'
        if self.type == self.TYPE_MARRIAGE:
            return 'fas fa-church'
        if self.type == self.TYPE_LOSS:
            return 'fas fa-cross'
        return ''

    def get_post_type_image_url(self):
        if self.type == self.TYPE_TRAVEL:
            return static('images/history_post_travel_bg.jpg')
        if self.type == self.TYPE_MARRIAGE:
            # Source: https://unsplash.com/photos/8vaQKYnawHw
            return static('images/history_post_marriage_bg.jpg')
        if self.type == self.TYPE_LOSS:
            # Source: https://unsplash.com/photos/9xEOFi3uGpM
            return static('images/history_post_loss_bg.jpg')
        return ''

    def get_absolute_url(self):
        return reverse('history:post_detail', args=[self.token])

    def get_post_date_display(self):
        return get_historical_date_display(self.post_date, self.post_date_precision)


class Group(TimeStampedModel):
    token = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        verbose_name='Título',
        max_length=500,
    )
    description = models.TextField('Descripción')

    image = models.ImageField(
        'Imagen', blank=True, null=True, upload_to='history/groups'
    )
    image_source_url = models.URLField(
        'Enlace a la fuente de la imagen', null=True, blank=True
    )

    admin_comments = models.TextField(
        'Comentarios de los administradores', default='', blank=True
    )

    members = models.ManyToManyField(
        'history.HistoricalFigure',
        related_name='groups',
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        verbose_name='Creado por',
        related_name='created_groups',
    )

    def get_absolute_url(self):
        return reverse('history:group_detail', args=[self.token])

    class Meta:
        verbose_name = 'Grupo histórico'
        verbose_name_plural = 'Grupos históricos'

    def __str__(self):
        return self.title
