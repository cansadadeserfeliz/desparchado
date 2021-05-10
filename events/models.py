import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.templatetags.static import static
from django.db.models import Q
from django.utils import timezone
from django.utils.html import format_html

from model_utils.models import TimeStampedModel
from autoslug import AutoSlugField

from desparchado.templatetags.desparchado_tags import format_currency


class EventQuerySet(models.QuerySet):
    def future(self):
        now = timezone.now()
        # Show multi-day events during only 5 days
        # after beginning
        return self.filter(
            (
                Q(event_date__gte=now) &
                Q(event_end_date__isnull=True)
            ) | (
                Q(event_end_date__gte=now) &
                Q(event_date__gte=now - datetime.timedelta(days=14))
            ),
        )

    def past(self):
        return self.exclude(
            (
                Q(event_date__gte=timezone.now()) &
                Q(event_end_date__isnull=True)
            ) | (
                Q(event_end_date__gte=timezone.now())
            ),
        )

    def published(self):
        return self.filter(
            is_published=True,
            is_approved=True,
        ).select_related('place', 'place__city')


class Event(TimeStampedModel):
    EVENT_TYPE_PUBLIC_LECTURE = 1
    EVENT_TYPE_DEBATE = 2
    EVENT_TYPE_MASTER_CLASS = 3
    EVENT_TYPE_TOUR = 4
    EVENT_TYPE_MEETING = 5
    EVENT_TYPE_THEATRICAL_PLAY = 6
    EVENT_TYPE_CONCERT = 7
    EVENT_TYPE_SEMINAR = 8
    EVENT_TYPE_EXHIBITION = 9
    EVENT_TYPE_FESTIVAL = 10
    EVENT_TYPE_MOVIES = 11

    EVENT_TYPES = (
        (EVENT_TYPE_PUBLIC_LECTURE, 'Conferencia pública'),
        (EVENT_TYPE_DEBATE, 'Debate'),
        (EVENT_TYPE_MASTER_CLASS, 'Taller'),
        (EVENT_TYPE_TOUR, 'Recorrido'),
        (EVENT_TYPE_MEETING, 'Encuentro'),
        (EVENT_TYPE_THEATRICAL_PLAY, 'Obra de teatro'),
        (EVENT_TYPE_CONCERT, 'Concierto'),
        (EVENT_TYPE_SEMINAR, 'Seminario'),
        (EVENT_TYPE_EXHIBITION, 'Exposición'),
        (EVENT_TYPE_FESTIVAL, 'Festival'),
        (EVENT_TYPE_MOVIES, 'Cine'),
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
    )
    slug = AutoSlugField(
        null=False, unique=True,
        populate_from='title',
    )

    description = models.TextField(
        verbose_name='Descripción',
        default='',
        help_text=format_html(
            'Puedes usar <a href="{}" target="_blank">Markdown</a> '
            'para dar formato al texto.',
            '/markdown',
        ),
    )
    event_type = models.PositiveSmallIntegerField(
        'Tipo del evento',
        null=True,
        blank=True,
        choices=EVENT_TYPES,
    )
    topic = models.PositiveSmallIntegerField(
        'Tema',
        null=True,
        blank=True,
        choices=EVENT_TOPICS,
    )
    event_date = models.DateTimeField(
        'Fecha del evento',
        db_index=True,
        help_text='p. ej. 23/11/2019 16:40',
    )
    event_end_date = models.DateTimeField(
        'Fecha final',
        null=True,
        blank=True,
        db_index=True,
        help_text='p. ej. 23/11/2019 18:00 (opcional)',
    )
    event_source_url = models.URLField(
        'Enlace a la página del evento',
        null=True,
        blank=False,
    )
    price = models.DecimalField(
        'Precio',
        default=0,
        decimal_places=2,
        max_digits=9
    )
    image = models.ImageField(
        'Imagen',
        blank=True,
        null=True,
        upload_to='events'
    )
    image_source_url = models.URLField(
        'Créditos/atribución de la imagen',
        null=True,
        blank=True
    )
    organizers = models.ManyToManyField(
        'events.Organizer',
        verbose_name='Organizadores',
        related_name='events',
        help_text=
        'Por favor, asegúrate de que el organizador que '
        'quieres asignar al evento '
        'no existe en nuestro sistema, antes de crearlo.',
    )
    place = models.ForeignKey(
        'places.Place', verbose_name='Lugar',
        related_name='events',
        on_delete=models.DO_NOTHING,
        db_index=True,
        help_text=
        'Por favor, asegúrate de que el lugar que '
        'quieres asignar al evento no existe en '
        'nuestro sistema, antes de crearlo.',
    )
    speakers = models.ManyToManyField(
        'events.Speaker', verbose_name='Presentadores',
        related_name='events',
        blank=True,
        help_text=
        'Por favor, asegúrate de que el presentador/la presentadora que '
        'quieres asignar al evento no existe en '
        'nuestro sistema, antes de crearlo/crearla.',
    )
    is_published = models.BooleanField(
        'Está publicado',
        default=True,
        help_text='Indica si el evento va a aparecer en la página',
    )
    is_approved = models.BooleanField(
        'Está aprobado', default=True,
        help_text='Campo de uso exclusivo para el administrador del sitio',
    )

    press_articles = models.ManyToManyField(
        'news.PressArticle',
        verbose_name='Artículos de prensa',
        related_name='events',
        blank=True,
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

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static('images/default_event_image.png')

    def get_absolute_url(self):
        return reverse('events:event_detail', args=[self.slug])

    def can_edit(self, user):
        if user.is_superuser or user == self.created_by or user in self.editors.all():
            return True
        return False

    @property
    def is_visible(self):
        return self.is_published and self.is_approved

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
    facebook_url = models.URLField('Página en Facebook', null=True, blank=True)
    twitter_url = models.URLField('Página en Twitter', null=True, blank=True)
    instagram_url = models.URLField('Página en Instagram', null=True, blank=True)
    image = models.ImageField(
        'Imagen', blank=True, null=True, upload_to='organizers')
    image_source_url = models.URLField(
        'Enlace a la fuente de la imagen', null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
    )
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='can_edit_organizers',
    )

    class Meta:
        verbose_name = 'Organizador'
        verbose_name_plural = 'Organizadores'

    def __str__(self):
        return self.name

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static('images/organizer-default.jpeg')

    def get_absolute_url(self):
        return reverse('events:organizer_detail', args=[self.slug])

    def can_edit(self, user):
        if user.is_superuser or user == self.created_by or user in self.editors.all():
            return True
        return False

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

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
    )
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='can_edit_speakers',
    )

    class Meta:
        verbose_name = 'Presentador'
        verbose_name_plural = 'Presentadores'

    def __str__(self):
        return self.name

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static('images/default_speaker_image.png')

    def get_absolute_url(self):
        return reverse('events:speaker_detail', args=[self.slug])

    def can_edit(self, user):
        if user.is_superuser or user == self.created_by or user in self.editors.all():
            return True
        return False

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains',)


class SocialNetworkPost(TimeStampedModel):
    event = models.ForeignKey(
        'events.Event',
        related_name='social_posts',
        on_delete=models.DO_NOTHING,
    )
    description = models.TextField(
        verbose_name='Descripción',
        help_text='Texto de publicación',
    )
    published_at = models.DateTimeField('Fecha de publicación')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return self.description

    class Meta:
        ordering = ('-published_at',)

    def clean(self):
        if self.published_at and not self.id:
            if self.published_at < timezone.now() - datetime.timedelta(minutes=30):
                raise ValidationError('You cannot set publish date in the past.')
        if self.published_at:
            if self.published_at > self.event.event_date:
                raise ValidationError('You cannot publish after event is started.')
