from django.contrib import admin

from .models import Special


@admin.register(Special)
class SpecialAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'slug',
        'is_published',
        'is_featured_on_homepage',
    ]

    raw_id_fields = ('related_events',)
