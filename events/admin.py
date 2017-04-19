from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Event, Organizer, Speaker


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):

    search_fields = ('title',)

    fieldsets = (
        (None, {
            'fields': (
                ('title', 'is_published',),
                ('slug', 'is_approved',)
            ),
        }),
        (_('Information'), {
            'fields': (
                'description',
                'event_source_url',
                'image',
                'image_source_url',
                ('event_type', 'topic'),
                ('event_date', 'event_end_date'),
                'price',
                'organizer',
                'place',
                'speakers',
            ),
        }),
    )

    ordering = ('-created', '-is_published')

    raw_id_fields = ('organizer', 'place', 'speakers')
    autocomplete_lookup_fields = {
        'fk': ['organizer', 'place'],
        'm2m': ['speakers'],
    }

    def get_actions(self, request):
        return []

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_list_display(self, request):
        list_display = [
            'title',
            'is_published',
            'is_approved',
            'event_type',
            'topic',
            'event_date',
            'event_end_date',
            'price',
            'created',
        ]
        if request.user.is_superuser:
            list_display.append('slug',)
            list_display.append('created_by')
            list_display.append('modified')
        return list_display

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['slug']
        if not request.user.is_superuser:
            readonly_fields.append('is_approved')
        return readonly_fields

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(created_by=request.user)
        return queryset

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and request.user == obj.created_by:
            return True
        if not obj:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description', 'created_by', 'created', 'modified')

    search_fields = ('name',)

    readonly_fields = ('slug',)

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'slug',
                'description',
                'website_url',
            ),
        }),
        ('Image', {
            'fields': (
                'image',
                'image_source_url',
            ),
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_actions(self, request):
        return []

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and request.user == obj.created_by:
            return True
        if not obj:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description', 'created_by', 'created', 'modified')

    search_fields = ('name',)

    readonly_fields = ('slug',)

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'slug',
                'description',
            ),
        }),
        ('Image', {
            'fields': (
                'image',
                'image_source_url',
            ),
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_actions(self, request):
        return []

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and request.user == obj.created_by:
            return True
        if not obj:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        return False
