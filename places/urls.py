from django.urls import path

from .views import (
    PlaceListView,
    PlaceDetailView,
    PlaceAutocomplete,
    PlaceCreateView,
    PlaceUpdateView,
    CityDetailView,
)


app_name = 'places'
urlpatterns = [
    path(
        '',
        PlaceListView.as_view(),
        name='place_list'
    ),
    path(
       'places-autocomplete/',
        PlaceAutocomplete.as_view(),
        name='place_autocomplete',
    ),

    path(
        'cities/<slug:slug>/',
        CityDetailView.as_view(),
        name='city_detail'
    ),

    path(
        'add/',
        PlaceCreateView.as_view(),
        name='place_add',
    ),

    path(
        '<int:pk>/',
        PlaceDetailView.as_view(),
        name='place_detail'
    ),
    path(
        '<slug:slug>/',
        PlaceDetailView.as_view(),
        name='place_detail'
    ),

    path(
        '<int:pk>/edit/',
        PlaceUpdateView.as_view(),
        name='place_update'
    ),
]
