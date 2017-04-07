from django.contrib.gis import admin as gis_admin
from django.contrib import admin

from .models import Place, City


@admin.register(Place)
class PlaceAdmin(gis_admin.OSMGeoAdmin):
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
