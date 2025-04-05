import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.utils import timezone

from model_utils.models import TimeStampedModel


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
