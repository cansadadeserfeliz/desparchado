from django.conf.urls import url

from .views import HomeView
from .views import EventsListView

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
]
