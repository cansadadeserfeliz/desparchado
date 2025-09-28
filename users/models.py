from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
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


class UserSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='settings',
    )
    event_creation_quota = models.PositiveIntegerField(default=10)
    organizer_creation_quota = models.PositiveIntegerField(default=5)
    speaker_creation_quota = models.PositiveIntegerField(default=5)
    place_creation_quota = models.PositiveIntegerField(default=5)
    quota_period_seconds = models.PositiveIntegerField(default=86400)  # 1 day

    def __str__(self):
        return f'{self.user.email} settings'

    def events_created_in_quota_period(self):
        since = now() - timedelta(seconds=self.quota_period_seconds)
        return self.user.created_events.filter(created__gte=since).count()

    def can_create_event(self):
        if self.user.is_superuser:
            return True, None

        count = self.events_created_in_quota_period()
        if count >= self.event_creation_quota:
            return False, (
                f"Quota reached: {self.event_creation_quota} events "
                f"every {self.quota_period_seconds} seconds."
            )
        return True, None


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create a UserSettings automatically when a new User is created.
    """
    if created:
        UserSettings.objects.get_or_create(user=instance)
