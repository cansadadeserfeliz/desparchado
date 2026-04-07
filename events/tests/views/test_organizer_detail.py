from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from events.tests.factories import EventFactory

VIEW_NAME = 'events:organizer_detail'


@pytest.mark.django_db
def test_show_details_of_organizer(django_app, organizer):
    response = django_app.get(
        reverse(VIEW_NAME, args=[organizer.slug]), status=200,
    )
    assert response.context['organizer'] == organizer
    assert organizer.name in response


@pytest.mark.django_db
def test_organizer_detail_future_events_contains_published_future_event(
    django_app, organizer,
):
    event = EventFactory(
        organizers=[organizer],
        event_date=timezone.now() + timedelta(days=1),
    )
    response = django_app.get(reverse(VIEW_NAME, args=[organizer.slug]), status=200)
    assert event in response.context['future_events']


@pytest.mark.django_db
def test_organizer_detail_past_events_contains_published_past_event(
    django_app, organizer,
):
    event = EventFactory(
        organizers=[organizer],
        event_date=timezone.now() - timedelta(days=1),
    )
    response = django_app.get(reverse(VIEW_NAME, args=[organizer.slug]), status=200)
    assert event in response.context['past_events']


@pytest.mark.django_db
def test_organizer_detail_unpublished_event_excluded_from_future_events(
    django_app, organizer,
):
    EventFactory(
        organizers=[organizer],
        event_date=timezone.now() + timedelta(days=1),
        is_published=False,
    )
    response = django_app.get(reverse(VIEW_NAME, args=[organizer.slug]), status=200)
    assert list(response.context['future_events']) == []


@pytest.mark.django_db
def test_organizer_detail_unpublished_event_excluded_from_past_events(
    django_app, organizer,
):
    EventFactory(
        organizers=[organizer],
        event_date=timezone.now() - timedelta(days=1),
        is_published=False,
    )
    response = django_app.get(reverse(VIEW_NAME, args=[organizer.slug]), status=200)
    assert list(response.context['past_events']) == []
