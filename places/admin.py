from django.contrib.gis import admin as gis_admin
from django.contrib import admin

from .models import Place, City

BOGOTA_LAT = 4.5930632
BOGOTA_LON = -74.0757637


@admin.register(Place)
class PlaceAdmin(gis_admin.OSMGeoAdmin):
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
    )

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and request.user == obj.created_by:
            return True
        if not obj:
            return True
        return False

    def get_list_display(self, request):
        list_display = list(self.list_display)
        if not request.user.is_superuser:
            list_display.remove('created_by')
        return list_display

    def get_actions(self, request):
        return []

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(City)
class CityAdmin(gis_admin.OSMGeoAdmin):

    def get_actions(self, request):
        return []

    def has_delete_permission(self, request, obj=None):
        return False
