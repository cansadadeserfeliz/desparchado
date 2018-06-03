from django.db import models

from model_utils.models import TimeStampedModel


class EventSource(TimeStampedModel):
    SOURCE_TYPE_FACEBOOK_EVENTS = 1
    SOURCE_TYPE_CUSTOM_WEBSITE = 2
    SOURCE_TYPES = (
        (None, 'Unknown'),
        (SOURCE_TYPE_CUSTOM_WEBSITE, 'Custom website'),
        (SOURCE_TYPE_FACEBOOK_EVENTS, 'Facebook events page'),
    )

    name = models.CharField('Nombre', max_length=255, unique=True)
    website_url = models.URLField('Página web', null=True, blank=True)
    source_type = models.PositiveSmallIntegerField(
        'Tipo del recurso',
        choices=SOURCE_TYPES,
    )

    def get_fb_page_url(self):
        if self.source_type != self.SOURCE_TYPE_FACEBOOK_EVENTS:
            return ''
        return self.website_url.replace('events/', '')




