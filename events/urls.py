from django.urls import path

import events.views as event_views

app_name = 'events'
urlpatterns = [
    # Future events list
    path('', event_views.EventListView.as_view(), name='event_list'),
    # Past events list
    path('past/', event_views.PastEventListView.as_view(), name='past_event_list'),
    # Add event
    path('add/', event_views.EventCreateView.as_view(), name='add_event'),
    # Update event
    path('<int:pk>/edit/', event_views.EventUpdateView.as_view(), name='event_update'),
    # Speakers
    path('speakers/', event_views.SpeakerListView.as_view(), name='speaker_list'),
    path('speakers/add/', event_views.SpeakerCreateView.as_view(), name='speaker_add'),
    path(
        'speaker-autocomplete/',
        event_views.SpeakerAutocomplete.as_view(),
        name='speaker_autocomplete',
    ),
    path(
        'speaker/<slug:slug>/',
        event_views.SpeakerDetailView.as_view(),
        name='speaker_detail',
    ),
    path(
        'speaker/<slug:slug>/edit/',
        event_views.SpeakerUpdateView.as_view(),
        name='speaker_update',
    ),
    # Organizations
    path('organizers/', event_views.OrganizerListView.as_view(), name='organizer_list'),
    path(
        'organizers/add/',
        event_views.OrganizerCreateView.as_view(),
        name='organizer_add',
    ),
    path(
        'organizers-autocomplete/',
        event_views.OrganizerAutocomplete.as_view(),
        name='organizer_autocomplete',
    ),
    path(
        'organizers-suggestions/',
        event_views.OrganizerSuggestionsView.as_view(),
        name='organizer_suggestions',
    ),
    path(
        'organizers/<slug:slug>/',
        event_views.OrganizerDetailView.as_view(),
        name='organizer_detail',
    ),
    path(
        'organizers/<slug:slug>/edit/',
        event_views.OrganizerUpdateView.as_view(),
        name='organizer_update',
    ),
    # Event detail views
    path('<int:pk>/', event_views.EventDetailView.as_view(), name='event_detail'),
    path('<slug:slug>/', event_views.EventDetailView.as_view(), name='event_detail'),
]
