from django.urls import path

from places.views.city_detail import CityDetailView
from places.views.place_autocomplete import PlaceAutocompleteView
from places.views.place_create import PlaceCreateView
from places.views.place_detail import PlaceDetailView
from places.views.place_list import PlaceListView
from places.views.place_update import PlaceUpdateView

app_name = 'places'
urlpatterns = [
    path('', PlaceListView.as_view(), name='place_list'),
    path(
        'places-autocomplete/',
        PlaceAutocompleteView.as_view(),
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
