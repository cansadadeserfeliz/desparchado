from django.contrib import admin

from .models import MediaSource
from .models import PressArticle


@admin.register(MediaSource)
class MediaSourceAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'slug',
    ]


@admin.register(PressArticle)
class PressArticleAdmin(admin.ModelAdmin):
    search_fields = ('title',)

    list_display = [
        'title',
        'source_url',
        'publication_date',
    ]
