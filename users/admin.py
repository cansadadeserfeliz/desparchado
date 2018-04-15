from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from .models import UserEventRelation

User = get_user_model()


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


admin.site.unregister(User)


@admin.register(User)
class MyUserAdmin(UserAdmin):

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset
