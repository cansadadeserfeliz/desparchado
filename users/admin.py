from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from .models import UserEventRelation
from .models import UserBadge
from .models import Badge

User = get_user_model()


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):

    list_display = [
        'user',
        'created',
    ]

    raw_id_fields = ('user', 'badge')


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'slug',
        'description',
        'created',
    ]

    def has_delete_permission(self, request, obj=None):
        return False


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

    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
        'is_superuser',
        'last_login',
    ]
