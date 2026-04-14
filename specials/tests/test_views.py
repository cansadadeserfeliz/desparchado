from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils.timezone import localtime, now

from events.models import Event
from events.tests.factories import EventFactory
from places.tests.factories import PlaceFactory
from specials.tests.factories import SpecialFactory


@pytest.mark.django_db
def test_successfully_show_special(django_app, special, event):
    assert special.related_events.count() == 3

    response = django_app.get(
        reverse('specials:special_detail', args=[special.slug]), status=200,
    )
    assert response.context['special'] == special

    assert response.context['filters']['selected_dates'] == []

    assert 'events' in response.context
    assert event in response.context['events']
    assert (
        len(response.context['events']) == 1
    ), 'only published event should be returned'


@pytest.mark.django_db
def test_does_not_show_not_published_special(django_app, special):
    special.is_published = False
    special.save()

    django_app.get(reverse('specials:special_detail', args=[special.slug]), status=404)


@pytest.mark.django_db
def test_filter_events_by_target_audience_on_special_page(django_app):
    matching = EventFactory(target_audience=Event.TargetAudience.PROFESSIONALS)
    other = EventFactory(target_audience=Event.TargetAudience.FAMILIES)
    special = SpecialFactory(related_events=[matching, other])

    response = django_app.get(
        reverse('specials:special_detail', args=[special.slug]),
        {
            'publico': 'professionals',
            'fecha': str(localtime(matching.event_date).date()),
        },
        status=200,
    )
    assert matching in response.context['events']
    assert other not in response.context['events']


@pytest.mark.django_db
def test_filter_events_by_target_audience_stacks_with_date(django_app):
    target_date = now() + timedelta(days=5)
    other_date = now() + timedelta(days=10)

    matching = EventFactory(
        target_audience=Event.TargetAudience.CHILDREN,
        event_date=target_date,
    )
    wrong_audience = EventFactory(
        target_audience=Event.TargetAudience.ADULTS,
        event_date=target_date,
    )
    wrong_date = EventFactory(
        target_audience=Event.TargetAudience.CHILDREN,
        event_date=other_date,
    )
    special = SpecialFactory(related_events=[matching, wrong_audience, wrong_date])

    response = django_app.get(
        reverse('specials:special_detail', args=[special.slug]),
        {
            'publico': 'children',
            'fecha': str(localtime(target_date).date()),
        },
        status=200,
    )
    assert matching in response.context['events']
    assert wrong_audience not in response.context['events']
    assert wrong_date not in response.context['events']


@pytest.mark.django_db
def test_filter_events_by_single_date(django_app):
    target_date = now() + timedelta(days=3)
    other_date = now() + timedelta(days=7)

    on_target = EventFactory(event_date=target_date)
    on_other = EventFactory(event_date=other_date)
    special = SpecialFactory(related_events=[on_target, on_other])

    response = django_app.get(
        reverse('specials:special_detail', args=[special.slug]),
        {'fecha': str(localtime(target_date).date())},
        status=200,
    )
    assert on_target in response.context['events']
    assert on_other not in response.context['events']


@pytest.mark.django_db
def test_filter_events_by_multiple_dates_returns_union(django_app):
    date_a = now() + timedelta(days=3)
    date_b = now() + timedelta(days=7)
    date_c = now() + timedelta(days=14)

    event_a = EventFactory(event_date=date_a)
    event_b = EventFactory(event_date=date_b)
    event_c = EventFactory(event_date=date_c)
    special = SpecialFactory(related_events=[event_a, event_b, event_c])

    response = django_app.get(
        reverse('specials:special_detail', args=[special.slug]),
        [
            ('fecha', str(localtime(date_a).date())),
            ('fecha', str(localtime(date_b).date())),
        ],
        status=200,
    )
    assert event_a in response.context['events']
    assert event_b in response.context['events']
    assert event_c not in response.context['events']


@pytest.mark.django_db
def test_invalid_fecha_value_is_ignored(django_app):
    target_date = now() + timedelta(days=3)
    event = EventFactory(event_date=target_date)
    special = SpecialFactory(related_events=[event])

    response = django_app.get(
        reverse('specials:special_detail', args=[special.slug]),
        [
            ('fecha', 'not-a-date'),
            ('fecha', str(localtime(target_date).date())),
        ],
        status=200,
    )
    assert event in response.context['events']
    selected = response.context['filters']['selected_dates']
    assert localtime(target_date).date() in selected



@pytest.mark.django_db
def test_search_and_date_filter_stack(django_app):
    target_date = now() + timedelta(days=3)
    other_date = now() + timedelta(days=7)

    match = EventFactory(title="Taller de pintura", event_date=target_date)
    wrong_date = EventFactory(title="Taller de pintura", event_date=other_date)
    wrong_title = EventFactory(title="Concierto de jazz", event_date=target_date)
    special = SpecialFactory(related_events=[match, wrong_date, wrong_title])

    response = django_app.get(
        reverse('specials:special_detail', args=[special.slug]),
        {'busqueda': 'taller', 'fecha': str(localtime(target_date).date())},
        status=200,
    )
    assert match in response.context['events']
    assert wrong_date not in response.context['events']
    assert wrong_title not in response.context['events']


@pytest.mark.django_db
def test_no_fecha_shows_all_events(django_app):
    event_a = EventFactory(event_date=now() + timedelta(days=1))
    event_b = EventFactory(event_date=now() + timedelta(days=10))
    special = SpecialFactory(related_events=[event_a, event_b])

    response = django_app.get(
        reverse('specials:special_detail', args=[special.slug]),
        status=200,
    )
    assert response.context['filters']['selected_dates'] == []
    assert event_a in response.context['events']
    assert event_b in response.context['events']


@pytest.mark.django_db
def test_filter_events_by_place(django_app):
    place_a = PlaceFactory()
    place_b = PlaceFactory()
    event_a = EventFactory(place=place_a)
    event_b = EventFactory(place=place_b)
    special = SpecialFactory(related_events=[event_a, event_b])

    response = django_app.get(
        reverse('specials:special_detail', args=[special.slug]),
        {'lugar': str(place_a.id)},
        status=200,
    )
    assert event_a in response.context['events']
    assert event_b not in response.context['events']


@pytest.mark.django_db
def test_invalid_lugar_value_is_ignored(django_app):
    event_a = EventFactory()
    event_b = EventFactory()
    special = SpecialFactory(related_events=[event_a, event_b])

    # Non-numeric value — parse error path
    response = django_app.get(
        reverse('specials:special_detail', args=[special.slug]),
        {'lugar': 'not-a-number'},
        status=200,
    )
    assert response.context['filters']['place_id'] is None
    assert event_a in response.context['events']
    assert event_b in response.context['events']

    # Numeric but nonexistent place ID — out-of-range path
    response2 = django_app.get(
        reverse('specials:special_detail', args=[special.slug]),
        {'lugar': '99999'},
        status=200,
    )
    assert response2.context['filters']['place_id'] is None
    assert event_a in response2.context['events']
    assert event_b in response2.context['events']


@pytest.mark.django_db
def test_filters_place_name_populated_for_valid_lugar(django_app):
    place = PlaceFactory(name="Teatro Mayor")
    event = EventFactory(place=place)
    special = SpecialFactory(related_events=[event])

    response = django_app.get(
        reverse('specials:special_detail', args=[special.slug]),
        {'lugar': str(place.id)},
        status=200,
    )
    filters = response.context['filters']
    assert filters['place_id'] == place.id
    assert filters['place_name'] == 'Teatro Mayor'


@pytest.mark.django_db
def test_filters_has_any_is_false_when_no_params(django_app):
    event = EventFactory()
    special = SpecialFactory(related_events=[event])

    response = django_app.get(
        reverse('specials:special_detail', args=[special.slug]),
        status=200,
    )
    assert response.context['filters']['has_any'] is False


@pytest.mark.django_db
def test_past_date_chip_has_chip_past_class(django_app):
    past_event = EventFactory(event_date=now() - timedelta(days=3))
    future_event = EventFactory(event_date=now() + timedelta(days=3))
    special = SpecialFactory(related_events=[past_event, future_event])

    response = django_app.get(
        reverse('specials:special_detail', args=[special.slug]),
        status=200,
    )
    html = response.text
    # Exactly one chip should carry the past modifier — not the future one
    assert html.count('chip--past') == 1
