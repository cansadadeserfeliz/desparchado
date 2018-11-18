from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from autoslug import AutoSlugField

from model_utils.models import TimeStampedModel


class UserEventRelation(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='events')
    event = models.ForeignKey('events.Event', related_name='user_relation')
    is_bookmarked = models.BooleanField(default=False)
    is_visited = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('User-Event Relation')
        verbose_name_plural = _('User-Event Relations')
        unique_together = ('user', 'event')


class UserBadge(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='badges')
    badge = models.ForeignKey('users.Badge', related_name='user_relation')
    description = models.TextField('Descripción', default='')

    class Meta:
        verbose_name = _('User-Badge Relation')
        verbose_name_plural = _('User-Badge Relations')
        unique_together = ('user', 'badge')


class Badge(TimeStampedModel):
    name = models.CharField('Nombre', max_length=255, unique=True)
    slug = AutoSlugField(null=False, unique=True, populate_from='name')
    description = models.TextField('Descripción', default='')
    image = models.ImageField(
        'Imagen',
        upload_to='badges'
    )

    def get_image_url(self):
        if self.image:
            return self.image.url
        return None
