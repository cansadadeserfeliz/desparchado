from django.conf.urls import url

from .views import HomeView
from .views import EventsListView
from .views import PlacesListView
from .views import UsersListView

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
    url(
        r'^users/$',
        UsersListView.as_view(),
        name='users'
    ),
]
