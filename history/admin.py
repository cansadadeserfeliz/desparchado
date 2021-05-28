from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import HistoricalFigure, Event, Post


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    model = Event

    list_display = [
        'title',
        'event_date',
        'event_end_date',
        'created_by',
        'created',
        'modified'
    ]

    fieldsets = (
        (None, {
            'fields': (
                'title',
            ),
        }),
        (_('Information and Sources'), {
            'fields': (
                'description',
                'sources',
                'image',
                'image_source_url',
            ),
        }),
        (_('Time and Place'), {
            'fields': (
                ('event_date', 'event_date_precision'),
                ('event_end_date', 'event_end_date_precision'),
                'location_name',
            ),
        }),
        (_('Historical Figures'), {
            'fields': (
                'historical_figures',
            ),
        }),
    )

    filter_horizontal = ('historical_figures',)

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    readonly_fields = ['created_by']


@admin.register(HistoricalFigure)
class HistoricalFigureAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'date_of_birth',
        'date_of_death',
        'created_by',
        'created',
        'modified',
    ]

    fieldsets = (
        (_('Name and Sources'), {
            'fields': (
                'name',
                'full_name',
                'sources',
                'image',
                'image_source_url',
            ),
        }),
        (_('Lifespan'), {
            'fields': (
                ('date_of_birth', 'date_of_birth_precision'),
                ('date_of_death', 'date_of_death_precision'),
            ),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    readonly_fields = ['created_by']


admin.site.register(Post)
