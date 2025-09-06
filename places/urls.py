from django.urls import path

from .views import (
    CityDetailView,
    PlaceAutocomplete,
    PlaceCreateView,
    PlaceDetailView,
    PlaceListView,
    PlaceUpdateView,
)

app_name = 'places'
urlpatterns = [
    path('', PlaceListView.as_view(), name='place_list'),
    path(
        'places-autocomplete/',
        PlaceAutocomplete.as_view(),
        name='place_autocomplete',
    ),
    path('cities/<slug:slug>/', CityDetailView.as_view(), name='city_detail'),
    path(
        'add/',
        PlaceCreateView.as_view(),
        name='place_add',
    ),
    path('<slug:slug>/', PlaceDetailView.as_view(), name='place_detail'),
    path('<int:pk>/edit/', PlaceUpdateView.as_view(), name='place_update'),
]
