from django.contrib import admin

from .models import HistoricalFigure, Event, Post, Group


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    search_fields = ('title',)

    list_select_related = ('created_by',)
    list_display = [
        'title',
        'event_date',
        'event_end_date',
        'created_by',
        'modified'
    ]
    date_hierarchy = 'event_date'

    fieldsets = (
        (None, {
            'fields': (
                'title',
            ),
        }),
        ('Details', {
            'fields': (
                'description',
                'sources',
                'admin_comments',
            ),
        }),
        ('Image', {
            'fields': (
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
    autocomplete_fields = ['historical_figures']
    readonly_fields = ['created_by']

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_actions(self, request):
        return []

    def has_delete_permission(self, request, obj=None):
        return False


class PostInline(admin.TabularInline):
    model = Post
    fields = (
        'type',
        'text',
        'post_date',
        'post_date_precision',
    )
    extra = 0
    can_delete = False


@admin.register(HistoricalFigure)
class HistoricalFigureAdmin(admin.ModelAdmin):
    search_fields = ('name',)

    list_select_related = ('created_by',)
    list_display = [
        'name',
        'date_of_birth',
        'date_of_death',
        'created_by',
        'modified',
    ]
    date_hierarchy = 'date_of_birth'

    fieldsets = (
        ('Basic info', {
            'fields': (
                'name',
                'full_name',
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
        ('Notes', {
            'fields': (
                'sources',
                'admin_comments',
            ),
        }),
    )
    readonly_fields = ['created_by']
    inlines = [PostInline]

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.created_by = request.user
            instance.save()
        formset.save_m2m()

    def get_actions(self, request):
        return []

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_select_related = ('historical_figure', 'created_by')
    list_display = [
        'historical_figure',
        'type',
        'post_date',
        'created_by',
        'modified',
    ]
    list_filter = ('type',)
    date_hierarchy = 'post_date'

    fieldsets = (
        ('Post Info', {
            'fields': (
                'historical_figure',
                'type',
                'text',
                'location_name',
                'image',
                'image_source_url',
            ),
        }),
        ('Post Date', {
            'fields': (
                ('post_date', 'post_date_precision'),
            ),
        }),
        ('Meta', {
            'fields': (
                'historical_figure_mentions',
                'published_in_groups',
            ),
        }),
        ('Notes', {
            'fields': (
                'sources',
                'admin_comments',
            ),
        }),
    )
    autocomplete_fields = [
        'historical_figure',
        'historical_figure_mentions',
        'published_in_groups',
    ]
    readonly_fields = ['created_by']

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_actions(self, request):
        return []

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    search_fields = ('title',)

    list_display = [
        'title',
        'modified',
    ]

    readonly_fields = ['created_by']
    autocomplete_fields = ['members']

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_actions(self, request):
        return []

    def has_delete_permission(self, request, obj=None):
        return False
