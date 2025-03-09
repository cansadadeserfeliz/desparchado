from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from autoslug import AutoSlugField

from model_utils.models import TimeStampedModel


class UserEventRelation(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='events',
        on_delete=models.DO_NOTHING,
    )
    event = models.ForeignKey(
        'events.Event',
        related_name='user_relation',
        on_delete=models.DO_NOTHING,
    )
    is_bookmarked = models.BooleanField(default=False)
    is_visited = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('User-Event Relation')
        verbose_name_plural = _('User-Event Relations')
        unique_together = ('user', 'event')
