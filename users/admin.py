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
        "event_quota_exceeded",
        "organizer_creation_quota",
        "speaker_creation_quota",
        "place_creation_quota",
        "place_quota_exceeded",
        "quota_period_human",
        "event_current_count",
    )
    search_fields = ("user__username", "user__email")
    list_select_related = ("user",)
    ordering = ("user__last_login",)
    list_per_page = 30

    def has_delete_permission(self, request, obj=None):
        """
        Disable deletion of objects from the admin interface.
        
        Returns:
            bool: `False` to prevent deletion of the object via the admin interface.
        """
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
        if seconds % 3600 == 0:  # divisible by hours
            return f"{seconds // 3600} hours"
        if seconds % 60 == 0:  # divisible by minutes
            return f"{seconds // 60} minutes"
        return f"{seconds} seconds"

    @admin.display(description="Events in Period")
    def event_current_count(self, obj):
        """
        Determines how many events the related user has created within the current quota period.
        
        Parameters:
            obj (UserSettings): The UserSettings instance whose user's events are counted.
        
        Returns:
            int: Number of events created by the user during the current quota period.
        """
        return obj.events_created_in_quota_period()

    @staticmethod
    def _get_quota_label(reached_quota: bool) -> str:
        """
        Render an HTML label indicating whether a quota has been reached.
        
        Returns:
        	An HTML-safe string containing a bold, colored label: "Exceeded" in red if `reached_quota` is True, "OK" in green otherwise.
        """
        color = "red" if reached_quota else "green"
        label = "Exceeded" if reached_quota else "OK"
        return format_html('<b style="color:{}">{}</b>', color, label)

    @admin.display(description="Events Quota Status")
    def event_quota_exceeded(self, obj):
        """
        Show quota status for the user's event-creation quota as a colored HTML label.
        
        Parameters:
            obj (UserSettings): The UserSettings instance for the row being displayed.
        
        Returns:
            str: HTML string containing a red "Exceeded" label if the event creation quota has been reached, otherwise a green "OK" label.
        """
        reached_quota = obj.reached_event_creation_quota()
        return self._get_quota_label(reached_quota)

    @admin.display(description="Places Quota Status")
    def place_quota_exceeded(self, obj):
        """
        Return an HTML label indicating whether the user's place-creation quota is exceeded.
        
        Parameters:
            obj (UserSettings): The UserSettings instance to evaluate.
        
        Returns:
            str: HTML string containing a colored label — "Exceeded" in red if the quota is reached, otherwise "OK" in green.
        """
        reached_quota = obj.reached_place_creation_quota()
        return self._get_quota_label(reached_quota)