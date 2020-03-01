from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from desparchado.utils import send_admin_notification
from .models import Event, Organizer, Speaker, SocialNetworkPost


@admin.register(SocialNetworkPost)
class SocialNetworkPostAdmin(admin.ModelAdmin):

    list_display = [
        'event',
        'description',
        'published_at',
    ]

    date_hierarchy = 'published_at'

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class SocialNetworkPostInline(admin.TabularInline):
    model = SocialNetworkPost
    fields = (
        'description',
        'published_at',
    )


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
                'organizers',
                'place',
                'speakers',
                'editors',
            ),
        }),
        (_('Extra'), {
            'fields': (
                'press_articles',
            ),
        }),
    )

    ordering = ('-created', '-is_published')

    raw_id_fields = (
        'place',
        'speakers',
        'press_articles',
        'organizers',
        'editors',
    )
    autocomplete_lookup_fields = {
        'fk': ['place'],
        'm2m': [
            'speakers',
            'organizers',
            'press_articles',
            'editors',
        ],
    }

    def get_actions(self, request):
        return []

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.created_by = request.user
            instance.save()
        formset.save_m2m()

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['slug']
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description', 'created_by', 'created', 'modified')

    search_fields = ('name',)

    readonly_fields = ('slug',)

    exclude = ('created_by',)

    raw_id_fields = (
        'editors',
    )
    autocomplete_lookup_fields = {
        'm2m': [
            'editors',
        ],
    }

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


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
        ('Related', {
            'fields': (
                'editors',
            ),
        }),
    )

    raw_id_fields = (
        'editors',
    )
    autocomplete_lookup_fields = {
        'm2m': [
            'editors',
        ],
    }

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
