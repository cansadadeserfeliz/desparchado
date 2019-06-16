from django.contrib import admin

from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):

    search_fields = ('title',)

    list_display = [
        'title',
        'slug',
        'is_published',
        'created',
    ]

    ordering = ('-created', '-is_published')

    raw_id_fields = (
        'related_events',
        'press_articles',
    )
    autocomplete_lookup_fields = {
        'm2m': [
            'related_events',
            'press_articles',
        ],
    }

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        return []
