from django.conf.urls import url

from .views import (
    PlaceListView,
    PlaceDetailView,
    PlaceAutocomplete,
    PlaceCreateView,
    PlaceUpdateView,
    CityDetailView,
)


urlpatterns = [
    url(
        r'^$',
        PlaceListView.as_view(),
        name='place_list'
    ),
    url(
        r'^places-autocomplete/$',
        PlaceAutocomplete.as_view(),
        name='place_autocomplete',
    ),

    url(
        r'^cities/(?P<slug>[\w-]+)/$',
        CityDetailView.as_view(),
        name='city_detail'
    ),

    url(
        r'^add/$',
        PlaceCreateView.as_view(),
        name='place_add',
    ),

    url(
        r'^(?P<pk>\d+)/$',
        PlaceDetailView.as_view(),
        name='place_detail'
    ),
    url(
        r'^(?P<slug>[\w-]+)/$',
        PlaceDetailView.as_view(),
        name='place_detail'
    ),

    url(
        r'^(?P<pk>\d+)/edit/$',
        PlaceUpdateView.as_view(),
        name='place_update'
    ),
]
