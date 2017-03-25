from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.templatetags.static import static

from model_utils.models import TimeStampedModel
from autoslug import AutoSlugField

from desparchado.templatetags.desparchado_tags import format_currency


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
        (EVENT_TYPE_PUBLIC_LECTURE, _('Public lecture')),
        (EVENT_TYPE_DEBATE, _('Debate')),
        (EVENT_TYPE_MASTER_CLASS, _('Master class')),
        (EVENT_TYPE_TOUR, _('Tour')),
        (EVENT_TYPE_MEETING, _('Meeting')),
        (EVENT_TYPE_THEATRICAL_PLAY, _('Theatrical play')),
        (EVENT_TYPE_CONCERT, _('Concert')),
        (EVENT_TYPE_SEMINAR, _('Seminar')),
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
        (EVENT_TOPIC_CITY, _('City')),
        (EVENT_TOPIC_SCIENCE, _('Science')),
        (EVENT_TOPIC_ART, _('Art')),
        (EVENT_TOPIC_BUSINESS, _('Business')),
        (EVENT_TOPIC_SOCIETY, _('Society')),
        (EVENT_TOPIC_HUMAN_SCIENCE, _('Human Science')),
        (EVENT_TOPIC_LANGUAGES, _('Languages')),
        (EVENT_TOPIC_LITERATURE, _('Literature')),
        (EVENT_TOPIC_ENVIRONMENT, _('Environment')),
        (EVENT_TOPIC_MEDICINE, _('Medicine')),
    )

    title = models.CharField(max_length=255)
    slug = AutoSlugField(
        null=True, default=None, unique=True, populate_from='title')

    description = models.TextField(default='')
    event_type = models.PositiveSmallIntegerField(choices=EVENT_TYPES)
    topic = models.PositiveSmallIntegerField(choices=EVENT_TOPICS)
    event_date = models.DateTimeField()
    event_end_date = models.DateTimeField(null=True, blank=True)
    event_source_url = models.URLField(null=True, blank=True)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=9)
    image = models.ImageField(blank=True, null=True, upload_to='events')
    image_source_url = models.URLField(null=True, blank=True)
    organizer = models.ForeignKey('events.Organizer')
    place = models.ForeignKey('places.Place')
    speakers = models.ManyToManyField('events.Speaker', blank=True, null=True)
    is_published = models.BooleanField(default=False)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.title

    def get_longitude_str(self):
        return self.place.get_longitude_str()

    def get_latitude_str(self):
        return self.place.get_latitude_str()

    def get_price_display(self):
        if self.price:
            return format_currency(self.price)
        return _('Free')

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static('images/default_event_image.jpg')

    @staticmethod
    def autocomplete_search_fields():
        return ('title__icontains',)

    class Meta:
        ordering = ('event_date',)


class Organizer(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(default='')
    website_url = models.URLField(null=True, blank=True)
    image = models.ImageField(blank=True, null=True, upload_to='organizers')
    image_source_url = models.URLField(null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

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
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(default='')
    image = models.ImageField(blank=True, null=True, upload_to='speakers')
    image_source_url = models.URLField(null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.name

    def get_image_url(self):
        if self.image:
            return self.image.url
        return None

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains',)
