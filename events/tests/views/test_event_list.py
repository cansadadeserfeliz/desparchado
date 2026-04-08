import pytest
from django.urls import reverse

from events.models import Event
from events.tests.factories import EventFactory

VIEW_NAME = 'events:event_list'


@pytest.mark.django_db
def test_events_appearance_in_event_list(
    django_app, event, not_published_event, not_approved_event, past_event,
):
    response = django_app.get(reverse(VIEW_NAME), status=200)

    assert event in response.context['events']
    assert not_published_event not in response.context['events']
    assert not_approved_event not in response.context['events']
    assert past_event not in response.context['events']


@pytest.mark.django_db
def test_filter_events_by_city_in_event_list(django_app, event, other_event):
    city_filter = event.place.city.slug
    response = django_app.get(
        reverse(VIEW_NAME), {'city': city_filter}, status=200,
    )
    assert event in response.context['events']
    assert other_event not in response.context['events']


@pytest.mark.django_db
def test_search_events_by_title(django_app, event, other_event):
    event.title = (
        'Después de la siesta, despertó con el rostro abuhado y los sueños revueltos'
    )
    event.save()

    response = django_app.get(
        reverse(VIEW_NAME), {'q': 'despues'}, status=200,
    )
    assert event in response.context['events']
    assert other_event not in response.context['events']


@pytest.mark.django_db
def test_search_events_speaker_name(django_app, event, speaker, other_event):
    speaker.name = 'Iñaki Rojas'
    speaker.save()
    event.speakers.add(speaker)

    response = django_app.get(reverse(VIEW_NAME), {'q': 'inaki'}, status=200)
    assert event in response.context['events']
    assert other_event not in response.context['events']


@pytest.mark.django_db
def test_filter_events_by_target_audience(django_app):
    matching = EventFactory(target_audience=Event.TargetAudience.CHILDREN)
    other = EventFactory(target_audience=Event.TargetAudience.ADULTS)

    response = django_app.get(
        reverse(VIEW_NAME), {'target_audience': 'children'}, status=200,
    )
    assert matching in response.context['events']
    assert other not in response.context['events']


@pytest.mark.django_db
def test_filter_events_by_target_audience_invalid_value_ignored(django_app):
    event = EventFactory(target_audience=Event.TargetAudience.CHILDREN)

    response = django_app.get(
        reverse(VIEW_NAME), {'target_audience': 'nonsense'}, status=200,
    )
    assert event in response.context['events']


@pytest.mark.django_db
def test_target_audience_choices_excludes_empty_values(django_app):
    EventFactory(target_audience='')

    response = django_app.get(reverse(VIEW_NAME), status=200)

    assert response.context['target_audience_choices'] == []


@pytest.mark.django_db
def test_target_audience_choices_present_when_events_have_value(django_app):
    EventFactory(target_audience=Event.TargetAudience.CHILDREN)

    response = django_app.get(reverse(VIEW_NAME), status=200)

    choices_values = [v for v, _ in response.context['target_audience_choices']]
    assert Event.TargetAudience.CHILDREN in choices_values
