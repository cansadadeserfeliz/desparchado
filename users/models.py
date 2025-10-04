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
        """
        Count events created by the user within the current quota period.
        
        The quota period is defined by `self.quota_period_seconds` measured backward from the current time.
        
        Returns:
            int: Number of events the user created since (now - quota_period_seconds).
        """
        since = now() - timedelta(seconds=self.quota_period_seconds)
        return self.user.created_events.filter(created__gte=since).count()

    def places_created_in_quota_period(self):
        """
        Return the number of places the user has created within the configured quota period.
        
        Returns:
            int: Count of places created by the user since now() minus `quota_period_seconds`.
        """
        since = now() - timedelta(seconds=self.quota_period_seconds)
        return self.user.created_places.filter(created__gte=since).count()

    def reached_event_creation_quota(self) ->  bool:
        """
        Determine whether the user has reached their allowed number of event creations within the configured quota period.
        
        Returns:
            True if the user has created greater than or equal to `event_creation_quota` events during the quota period; `False` otherwise. Superusers always bypass the quota and will return `False`.
        """
        if self.user.is_superuser:
            return False

        count = self.events_created_in_quota_period()
        if count >= self.event_creation_quota:
            return True
        return False

    def reached_place_creation_quota(self) ->  bool:
        """
        Determine whether the user has reached their place creation quota.
        
        Superusers are exempt and always considered not to have reached the quota.
        
        Returns:
            True if the user has reached the place creation quota, False otherwise.
        """
        if self.user.is_superuser:
            return False

        count = self.places_created_in_quota_period()
        if count >= self.place_creation_quota:
            return True
        return False


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a UserSettings record when a new User is created.
    
    Parameters:
        sender (type): The model class sending the signal (User).
        instance (User): The User instance that was saved.
        created (bool): True if the instance was created (not just updated).
        **kwargs: Additional keyword arguments passed by the signal.
    """
    if created:
        UserSettings.objects.get_or_create(user=instance)