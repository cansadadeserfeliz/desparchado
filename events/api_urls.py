from django.urls import path

from events.api.views import (
    EventCreateAPIView,
    EventListAPIView,
    FutureEventListAPIView,
)

app_name = 'events'  # pylint: disable=invalid-name

urlpatterns = [
    path(
        route="events/",
        view=EventListAPIView.as_view(),
        name="events_list",
    ),
    path(
        route="events/future/",
        view=FutureEventListAPIView.as_view(),
        name="future_events_list",
    ),
    path(
        route="events/create/",
        view=EventCreateAPIView.as_view(),
        name="event_create",
    ),
]
