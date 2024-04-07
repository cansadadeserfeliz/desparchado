from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, Group, Permission

from autoslug import AutoSlugField

from model_utils.models import TimeStampedModel


class User(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="custom_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="custom_user_set",
        related_query_name="user",
    )


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


class UserBadge(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='badges',
        on_delete=models.DO_NOTHING,
    )
    badge = models.ForeignKey(
        'users.Badge',
        related_name='user_relation',
        on_delete=models.DO_NOTHING,
    )
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
