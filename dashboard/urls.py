from django.conf.urls import url

from .views import HomeView
from .views import EventsListView
from .views import PlacesListView

urlpatterns = [
    url(
        r'^$',
        HomeView.as_view(),
        name='home'
    ),
    url(
        r'^events/$',
        EventsListView.as_view(),
        name='events'
    ),
    url(
        r'^places/$',
        PlacesListView.as_view(),
        name='places'
    ),
]
