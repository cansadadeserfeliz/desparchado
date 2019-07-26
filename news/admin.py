from django.contrib import admin

from .models import MediaSource
from .models import PressArticle


@admin.register(MediaSource)
class MediaSourceAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'slug',
        'source_type',
        'website_url',
        'description',
    ]


@admin.register(PressArticle)
class PressArticleAdmin(admin.ModelAdmin):
    search_fields = ('title',)

    list_select_related = ('media_source',)

    list_display = [
        'title',
        'slug',
        'source_url',
        'media_source',
        'publication_date',
    ]
