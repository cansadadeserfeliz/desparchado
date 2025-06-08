from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from events.tests.factories import EventFactory
from places.tests.factories import CityFactory, PlaceFactory


@pytest.mark.django_db
# pylint: disable=too-many-arguments,too-many-positional-arguments
def test_events_appearance_in_future_event_list(
    client,
    future_event,
    featured_future_event,
    not_published_event,
    not_approved_event,
    past_event,
):
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

    # Verify all serializer fields
    assert 'formatted_hour' in event_data
    assert 'formatted_day' in event_data
    assert 'place' in event_data
    assert 'name' in event_data['place']
    assert 'slug' in event_data['place']
    assert 'image_url' in event_data
    assert 'truncated_description' in event_data
    assert 'is_recurrent' in event_data
    assert event_data['title'] == future_event.title
    assert event_data['slug'] == future_event.slug
    assert event_data['url'] == future_event.get_absolute_url()


@pytest.mark.django_db
def test_future_event_list_ordering_by_event_date(client):
    future_event_1 = EventFactory(
        event_date=timezone.now() + timedelta(days=1),
        place=PlaceFactory(
            city=CityFactory(),
        ),
    )
    future_event_2 = EventFactory(
        event_date=timezone.now() + timedelta(days=2),
        place=PlaceFactory(
            city=CityFactory(),
        ),
    )

    response = client.get(
        reverse('events_api:future_events_list'),
        query_params={
            'ordering': 'event_date',
        },
    )
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()

    assert 'results' in json_response
    assert len(json_response['results']) == 2

    assert json_response['results'][0]['title'] == future_event_1.title
    assert json_response['results'][1]['title'] == future_event_2.title

    response = client.get(
        reverse('events_api:future_events_list'),
        query_params={
            'ordering': '-event_date',
        },
    )
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()

    assert 'results' in json_response
    assert len(json_response['results']) == 2

    assert json_response['results'][0]['title'] == future_event_2.title
    assert json_response['results'][1]['title'] == future_event_1.title


@pytest.mark.django_db
def test_future_event_list_filter_by_city(client):
    future_event_1 = EventFactory(
        event_date=timezone.now() + timedelta(days=1),
        place=PlaceFactory(
            city=CityFactory(),
        ),
    )
    future_event_2 = EventFactory(
        event_date=timezone.now() + timedelta(days=1),
        place=PlaceFactory(
            city=CityFactory(),
        ),
    )

    response = client.get(
        reverse('events_api:future_events_list'),
        query_params={
            'place__city__slug': future_event_1.place.city.slug,
        },
    )
    assert response.status_code == status.HTTP_200_OK

    json_response = response.json()

    assert 'results' in json_response
    assert len(json_response['results']) == 1
    event_data = json_response['results'][0]

    assert event_data['title'] == future_event_1.title
    assert event_data['slug'] == future_event_1.slug

    response = client.get(
        reverse('events_api:future_events_list'),
        query_params={
            'place__city__slug': future_event_2.place.city.slug,
        },
    )
    assert response.status_code == status.HTTP_200_OK

    json_response = response.json()

    assert 'results' in json_response
    assert len(json_response['results']) == 1
    event_data = json_response['results'][0]

    assert event_data['title'] == future_event_2.title
    assert event_data['slug'] == future_event_2.slug
