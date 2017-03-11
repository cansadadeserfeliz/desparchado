from django.contrib.gis import admin as gis_admin
from django.contrib import admin

from .models import Place, City


@admin.register(Place)
class PlaceAdmin(gis_admin.OSMGeoAdmin):
    list_display = (
        'name', 'location', 'description', 'city', 'created_by',
        'created', 'modified',
    )

    search_fields = ('name',)

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'description',
                'city',
                'location',
            ),
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(City)
class CityAdmin(gis_admin.OSMGeoAdmin):
    pass
