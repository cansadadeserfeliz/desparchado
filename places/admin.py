from django.contrib.gis import admin as gis_admin
from django.contrib import admin

from .models import Place, City


@admin.register(Place)
class PlaceAdmin(gis_admin.OSMGeoAdmin):
    list_display = ('name', 'location', 'city')


@admin.register(City)
class CityAdmin(gis_admin.OSMGeoAdmin):
    pass
