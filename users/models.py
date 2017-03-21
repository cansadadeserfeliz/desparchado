from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel


class UserEventRelation(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    event = models.ForeignKey('events.Event')
    is_bookmarked = models.BooleanField(default=False)
    is_visited = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('User-Event Relation')
        verbose_name_plural = _('User-Event Relations')
        unique_together = ('user', 'event')
