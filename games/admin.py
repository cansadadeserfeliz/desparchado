from django.contrib import admin

from .models import HuntingOfSnarkCategory, HuntingOfSnarkCriteria, HuntingOfSnarkGame


@admin.register(HuntingOfSnarkGame)
class HuntingOfSnarkGameAdmin(admin.ModelAdmin):
    search_fields = [
        'token',
        'player_name',
    ]
    list_display = [
        'token',
        'player_name',
        'total_points',
        'created',
    ]

    raw_id_fields = ('criteria',)


@admin.register(HuntingOfSnarkCriteria)
class HuntingOfSnarkCriteriaAdmin(admin.ModelAdmin):
    search_fields = [
        'public_id',
        'name',
    ]
    list_display = [
        'public_id',
        'name',
        'category',
        'created',
        'modified',
    ]
    list_select_related = ['category']


@admin.register(HuntingOfSnarkCategory)
class HuntingOfSnarkCategoryAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
    ]
    list_display = [
        'name',
        'order',
        'created',
        'modified',
    ]
