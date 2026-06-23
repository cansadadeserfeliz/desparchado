from django.urls import path

from places.api.views import PlaceCreateAPIView, PlaceSearchAPIView

app_name = 'places_api'

urlpatterns = [
    path(
        route='places/search/',
        view=PlaceSearchAPIView.as_view(),
        name='place_search',
    ),
    path(
        route='places/create/',
        view=PlaceCreateAPIView.as_view(),
        name='place_create',
    ),
]
