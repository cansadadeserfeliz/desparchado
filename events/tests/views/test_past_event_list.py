import pytest
from django.urls import reverse

VIEW_NAME = 'events:past_event_list'


@pytest.mark.django_db
def test_events_appearance_in_past_event_list(
    django_app, event, not_published_event, not_approved_event, past_event,
):
    response = django_app.get(reverse(VIEW_NAME), status=200)

    assert past_event in response.context['events']
    assert event not in response.context['events']
    assert not_published_event not in response.context['events']
    assert not_approved_event not in response.context['events']
