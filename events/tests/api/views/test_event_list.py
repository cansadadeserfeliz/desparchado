from datetime import timedelta

import pytest

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from ...factories import SpeakerFactory
from ....models import Event
from ....models import Organizer
from ....models import Speaker


@pytest.mark.django_db
def test_events_appearance_in_future_event_list(client, future_event, featured_future_event, not_published_event, not_approved_event, past_event):
    response = client.get(reverse('events_api:future_events_list'))
    assert response.status_code == status.HTTP_200_OK

    json_response = response.json()

    assert 'results' in json_response
    event_titles = [event_data['title'] for event_data in json_response['results']]
    assert not_published_event.title not in event_titles
    assert not_approved_event.title not in event_titles
    assert past_event.title not in event_titles
    assert future_event.title in event_titles
    assert featured_future_event.title in event_titles


@pytest.mark.django_db
def test_future_event_list_payload(client, future_event):
    response = client.get(reverse('events_api:future_events_list'))
    assert response.status_code == status.HTTP_200_OK

    json_response = response.json()

    assert 'results' in json_response
    assert len(json_response['results']) == 1
    event_data = json_response['results'][0]

    assert event_data['title'] == future_event.title
    assert event_data['slug'] == future_event.slug
    assert event_data['url'] == future_event.get_absolute_url()
