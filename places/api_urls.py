from django.urls import path

from places.api.views import PlaceSearchAPIView

app_name = 'places_api'

urlpatterns = [
    path(
        route='places/search/',
        view=PlaceSearchAPIView.as_view(),
        name='place_search',
    ),
]
