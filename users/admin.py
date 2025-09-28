from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import UserEventRelation, UserSettings

User = get_user_model()


@admin.register(UserEventRelation)
class UserEventRelationAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'is_bookmarked',
        'is_visited',
    )

    raw_id_fields = ('user', 'event')

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.unregister(User)


@admin.register(User)
class MyUserAdmin(UserAdmin):
    date_hierarchy = "last_login"
    ordering = ("date_joined",)

    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',
        'last_login',
    ]


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    """
    Displays users with their record creation quota, the quota period in a
    human-readable format, the current number of records created within
    that period and whether the quota has been exceeded.
    """
    list_display = (
        "user",
        "user_is_superuser",
        "event_creation_quota",
        "organizer_creation_quota",
        "speaker_creation_quota",
        "place_creation_quota",
        "quota_period_human",
        "event_current_count",
        "event_quota_exceeded",
    )
    search_fields = ("user__username", "user__email")
    select_related = ("user",)
    ordering = ("user__last_login",)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Disable delete
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions

    @admin.display(description="Superuser", boolean=True)
    def user_is_superuser(self, obj):
        return obj.user.is_superuser

    @admin.display(description="Quota Period")
    def quota_period_human(self, obj):
        """Convert seconds into a friendlier unit."""
        seconds = obj.quota_period_seconds
        if seconds % 86400 == 0:  # divisible by days
            return f"{seconds // 86400} days"
        elif seconds % 3600 == 0:  # divisible by hours
            return f"{seconds // 3600} hours"
        elif seconds % 60 == 0:  # divisible by minutes
            return f"{seconds // 60} minutes"
        return f"{seconds} seconds"

    @admin.display(description="Events in Period")
    def event_current_count(self, obj):
        """
        Return the number of events the user has created within
        the current quota period.
        """
        return obj.events_created_in_quota_period()

    @admin.display(description="Events Quota Status")
    def event_quota_exceeded(self, obj):
        """Indicate whether the user's event creation quota has been exceeded."""
        can_create, _ = obj.can_create_event()
        color = "red" if not can_create else "green"
        label = "Exceeded" if not can_create else "OK"
        return format_html('<b style="color:{}">{}</b>', color, label)
