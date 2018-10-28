from django.conf.urls import url

import events.views as event_views


urlpatterns = [
    # Future events list
    url(
        r'^$',
        event_views.EventListView.as_view(),
        name='event_list'
    ),

    # Past events list
    url(
        r'^past/$',
        event_views.PastEventListView.as_view(),
        name='past_event_list'
    ),

    # Add event
    url(
        r'^add/$',
        event_views.EventCreateView.as_view(),
        name='add_event'
    ),

    # Update event
    url(
        r'^(?P<pk>\d+)/edit/$',
        event_views.EventUpdateView.as_view(),
        name='event_update'
    ),

    # Speakers
    url(
        r'^speakers/$',
        event_views.SpeakerListView.as_view(),
        name='speaker_list'
    ),
    url(
        r'^speakers/add/$',
        event_views.SpeakerCreateView.as_view(),
        name='speaker_add'
    ),
    url(
        r'^speaker-autocomplete/$',
        event_views.SpeakerAutocomplete.as_view(),
        name='speaker_autocomplete',
    ),
    url(
        r'^speaker/(?P<slug>[\w-]+)/$',
        event_views.SpeakerDetailView.as_view(),
        name='speaker_detail'
    ),
    url(
        r'^speaker/(?P<slug>[\w-]+)/edit/$',
        event_views.SpeakerUpdateView.as_view(),
        name='speaker_update'
    ),

    # Organizations
    url(
        r'^organizers/$',
        event_views.OrganizerListView.as_view(),
        name='organizer_list'
    ),
    url(
        r'^organizers/add/$',
        event_views.OrganizerCreateView.as_view(),
        name='organizer_add'
    ),
    url(
        r'^organizers-autocomplete/$',
        event_views.OrganizerAutocomplete.as_view(),
        name='organizer_autocomplete',
    ),
    url(
        r'^organizers/(?P<slug>[\w-]+)/$',
        event_views.OrganizerDetailView.as_view(),
        name='organizer_detail'
    ),
    url(
        r'^organizers/(?P<pk>\d+)/edit/$',
        event_views.OrganizerUpdateView.as_view(),
        name='organizer_update'
    ),

    # Event detail views
    url(
        r'^(?P<pk>\d+)/$',
        event_views.EventDetailView.as_view(),
        name='event_detail'
    ),
    url(
        r'^(?P<slug>[\w-]+)/$',
        event_views.EventDetailView.as_view(),
        name='event_detail'
    ),


]
