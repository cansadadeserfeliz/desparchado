from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import UserEventRelation

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
