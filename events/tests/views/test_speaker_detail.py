from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from events.tests.factories import EventFactory

VIEW_NAME = 'events:speaker_detail'


@pytest.mark.django_db
def test_successfully_show_details_of_speaker(django_app, speaker):
    response = django_app.get(
        reverse(VIEW_NAME, args=[speaker.slug]), status=200,
    )
    assert response.context['speaker'] == speaker


@pytest.mark.django_db
def test_speaker_detail_404(django_app):
    django_app.get(reverse(VIEW_NAME, args=['no-such-speaker']), status=404)


@pytest.mark.django_db
def test_speaker_detail_future_events_contains_published_future_event(
    django_app, speaker,
):
    event = EventFactory(
        speakers=[speaker],
        event_date=timezone.now() + timedelta(days=1),
    )
    response = django_app.get(reverse(VIEW_NAME, args=[speaker.slug]), status=200)
    assert event in response.context['future_events']


@pytest.mark.django_db
def test_speaker_detail_past_events_contains_published_past_event(
    django_app, speaker,
):
    event = EventFactory(
        speakers=[speaker],
        event_date=timezone.now() - timedelta(days=1),
    )
    response = django_app.get(reverse(VIEW_NAME, args=[speaker.slug]), status=200)
    assert event in response.context['past_events']


@pytest.mark.django_db
def test_speaker_detail_unpublished_event_excluded_from_future_events(
    django_app, speaker,
):
    EventFactory(
        speakers=[speaker],
        event_date=timezone.now() + timedelta(days=1),
        is_published=False,
    )
    response = django_app.get(reverse(VIEW_NAME, args=[speaker.slug]), status=200)
    assert list(response.context['future_events']) == []


@pytest.mark.django_db
def test_speaker_detail_unpublished_event_excluded_from_past_events(
    django_app, speaker,
):
    EventFactory(
        speakers=[speaker],
        event_date=timezone.now() - timedelta(days=1),
        is_published=False,
    )
    response = django_app.get(reverse(VIEW_NAME, args=[speaker.slug]), status=200)
    assert list(response.context['past_events']) == []
