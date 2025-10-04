from django.urls import path

from events.views.event_create import EventCreateView
from events.views.event_detail import EventDetailView
from events.views.event_list import EventListView, PastEventListView
from events.views.event_update import EventUpdateView
from events.views.organizer_autocomplete import OrganizerAutocompleteView
from events.views.organizer_create import OrganizerCreateView
from events.views.organizer_detail import OrganizerDetailView
from events.views.organizer_list import OrganizerListView
from events.views.organizer_suggestion import OrganizerSuggestionsView
from events.views.organizer_update import OrganizerUpdateView
from events.views.speaker_autocomplete import SpeakerAutocomplete
from events.views.speaker_create import SpeakerCreateView
from events.views.speaker_detail import SpeakerDetailView
from events.views.speaker_list import SpeakerListView
from events.views.speaker_update import SpeakerUpdateView

app_name = 'events'  # pylint: disable=invalid-name

urlpatterns = [
    # Future events list
    path('', EventListView.as_view(), name='event_list'),
    # Past events list
    path('past/', PastEventListView.as_view(), name='past_event_list'),
    # Add event
    path('add/', EventCreateView.as_view(), name='add_event'),
    # Update event
    path('<int:pk>/edit/', EventUpdateView.as_view(), name='event_update'),
    # Speakers
    path('speakers/', SpeakerListView.as_view(), name='speaker_list'),
    path('speakers/add/', SpeakerCreateView.as_view(), name='speaker_add'),
    path(
        'speaker-autocomplete/',
        SpeakerAutocomplete.as_view(),
        name='speaker_autocomplete',
    ),
    path(
        'speaker/<slug:slug>/',
        SpeakerDetailView.as_view(),
        name='speaker_detail',
    ),
    path(
        'speaker/<slug:slug>/edit/',
        SpeakerUpdateView.as_view(),
        name='speaker_update',
    ),
    # Organizations
    path('organizers/', OrganizerListView.as_view(), name='organizer_list'),
    path(
        'organizers/add/',
        OrganizerCreateView.as_view(),
        name='organizer_add',
    ),
    path(
        'organizers-autocomplete/',
        OrganizerAutocompleteView.as_view(),
        name='organizer_autocomplete',
    ),
    path(
        'organizers-suggestions/',
        OrganizerSuggestionsView.as_view(),
        name='organizer_suggestions',
    ),
    path(
        'organizers/<slug:slug>/',
        OrganizerDetailView.as_view(),
        name='organizer_detail',
    ),
    path(
        'organizers/<slug:slug>/edit/',
        OrganizerUpdateView.as_view(),
        name='organizer_update',
    ),
    # Event detail views
    path(
        '<slug:slug>/',
        EventDetailView.as_view(),
        name='event_detail',
    ),
]
