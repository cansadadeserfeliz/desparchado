from django.urls import path

from events.views.api.event_create import EventCreateAPIView
from events.views.api.event_list import EventListAPIView, FutureEventListAPIView
from events.views.api.organizer_search import OrganizerSearchAPIView
from events.views.api.speaker_search import SpeakerSearchAPIView

app_name = 'events'  # pylint: disable=invalid-name

urlpatterns = [
    path(route='events/', view=EventListAPIView.as_view(), name='event_list'),
    path(
        route='events/create/',
        view=EventCreateAPIView.as_view(),
        name='event_create',
    ),
    path(
        route='events/future/',
        view=FutureEventListAPIView.as_view(),
        name='future_events_list',
    ),
    path(
        route='organizers/search/',
        view=OrganizerSearchAPIView.as_view(),
        name='organizer_search',
    ),
    path(
        route='speakers/search/',
        view=SpeakerSearchAPIView.as_view(),
        name='speaker_search',
    ),
]
