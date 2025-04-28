from django.urls import path

from events.api.views import (
    EventListAPIView,
    FutureEventListAPIView,
)


app_name = 'events'
urlpatterns = [
    path(
        route='events/',
        view=EventListAPIView.as_view(),
        name='events_list'
    ),
    path(
        route='events/future/',
        view=FutureEventListAPIView.as_view(),
        name='future_events_list'
    ),
]
