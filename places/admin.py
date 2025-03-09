from django.contrib.gis.db import models as geo_models
from django.contrib import admin

import mapwidgets

from .models import Place, City

BOGOTA_LAT = 4.5930632
BOGOTA_LON = -74.0757637


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    default_lat = BOGOTA_LAT
    default_lon = BOGOTA_LON
    default_zoom = 6

    list_display = (
        'name', 'slug', 'location', 'description', 'city', 'created_by',
        'created', 'modified',
    )

    readonly_fields = ('slug',)

    search_fields = ('name',)

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'slug',
                'description',
                'city',
                'location',
            ),
        }),
        ('Image', {
            'fields': (
                'image',
                'image_source_url',
            ),
        }),
        ('Related', {
            'fields': (
                'editors',
            ),
        }),
    )

    raw_id_fields = (
        'editors',
    )

    formfield_overrides = {
        geo_models.PointField: {'widget': mapwidgets.GoogleMapPointFieldWidget()}
    }

    def get_actions(self, request):
        return []

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'slug',
        'description',
    ]

    def get_actions(self, request):
        return []

    def has_delete_permission(self, request, obj=None):
        return False

    formfield_overrides = {
        geo_models.PointField: {'widget': mapwidgets.GoogleMapPointFieldWidget()}
    }
