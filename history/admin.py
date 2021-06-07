from django.contrib import admin

from .models import HistoricalFigure, Event, Post


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    search_fields = ('title',)

    list_select_related = ('created_by',)

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
        ('Information and Sources', {
            'fields': (
                'description',
                'sources',
                'image',
                'image_source_url',
            ),
        }),
        ('Time and Place', {
            'fields': (
                ('event_date', 'event_date_precision'),
                ('event_end_date', 'event_end_date_precision'),
                'location_name',
            ),
        }),
        ('Historical Figures', {
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
    search_fields = ('name',)

    list_select_related = ('created_by',)

    list_display = [
        'name',
        'date_of_birth',
        'date_of_death',
        'created_by',
        'created',
        'modified',
    ]

    fieldsets = (
        ('Name and Sources', {
            'fields': (
                'name',
                'full_name',
                'sources',
                'image',
                'image_source_url',
            ),
        }),
        ('Lifespan', {
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


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_select_related = ('historical_figure', 'created_by')

    list_display = [
        'historical_figure',
        'type',
        'post_date',
        'created_by',
        'created',
    ]

    list_filter = ('post_date',)

    fieldsets = (
        ('Post Info', {
            'fields': (
                'historical_figure',
                'type',
                'text',
                'sources',
                'image',
                'image_source_url',
            ),
        }),
        ('Post Date', {
            'fields': (
                ('post_date', 'post_date_precision'),
            ),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    readonly_fields = ['created_by']
