from django.contrib import admin

from .models import EventSource


@admin.register(EventSource)
class EventSourceAdmin(admin.ModelAdmin):

    search_fields = ('name',)

    list_display = [
        'name',
        'source_type',
        'website_url',
    ]
