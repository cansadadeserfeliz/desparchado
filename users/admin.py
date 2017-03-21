from django.contrib import admin

from .models import UserEventRelation


@admin.register(UserEventRelation)
class UserEventRelationAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'event',
        'is_bookmarked',
        'is_visited',
    )

    def has_delete_permission(self, request, obj=None):
        return False
