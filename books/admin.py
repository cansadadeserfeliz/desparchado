from django.contrib import admin

from .models import Book
from .models import Author


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):

    search_fields = ('title',)

    list_display = [
        'title',
        'slug',
        'isbn',
        'is_published',
        'created',
    ]

    ordering = ('-created', '-is_published')

    raw_id_fields = (
        'related_events',
        'press_articles',
        'authors',
        'blog_posts',
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        return []


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):

    search_fields = ('name',)

    list_display = [
        'name',
        'slug',
        'created',
    ]

    raw_id_fields = (
        'speaker',
    )
