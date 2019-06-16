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
    list_display = [
        'title',
        'source_url',
    ]
