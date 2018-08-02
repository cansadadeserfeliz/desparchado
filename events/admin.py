from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from desparchado.utils import send_admin_notification
from .models import Event, Organizer, Speaker, SocialNetworkPost


class SocialNetworkPostInline(admin.TabularInline):
    model = SocialNetworkPost


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):

    search_fields = ('title',)

    list_display = [
        'title',
        'is_published',
        'is_approved',
        'event_type',
        'topic',
        'event_date',
        'event_end_date',
        'created_by',
        'created',
    ]

    inlines = [SocialNetworkPostInline]

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
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['slug']
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SocialNetworkPost)
class SocialNetworkPostAdmin(admin.ModelAdmin):
    list_display = (
        'description',
        'published_at',
        'event',
    )

    raw_id_fields = ('event',)
    autocomplete_lookup_fields = {
        'fk': ['event'],
    }

    ordering = ('-published_at',)


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
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

        send_admin_notification(request, obj, form, change)

    def get_actions(self, request):
        return []

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
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

        send_admin_notification(request, obj, form, change)

    def get_actions(self, request):
        return []

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return False
