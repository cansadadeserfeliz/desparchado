from django.contrib import admin

from .models import HuntingOfSnarkGame
from .models import HuntingOfSnarkCriteria
from .models import HuntingOfSnarkCategory


@admin.register(HuntingOfSnarkGame)
class HuntingOfSnarkGameAdmin(admin.ModelAdmin):
    list_display = [
        'token',
        'player_name',
        'total_points',
    ]


@admin.register(HuntingOfSnarkCriteria)
class HuntingOfSnarkCriteriaAdmin(admin.ModelAdmin):
    list_display = [
        'public_id',
        'name',
    ]


@admin.register(HuntingOfSnarkCategory)
class HuntingOfSnarkCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name',
    ]
