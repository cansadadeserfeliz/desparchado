import pytest
from django.urls import reverse
from django.utils.timezone import localtime


@pytest.mark.django_db
def test_successfully_show_special(django_app, special, event):
    assert special.related_events.count() == 3

    response = django_app.get(
        reverse('specials:special_detail', args=[special.slug]), status=200,
    )
    assert response.context['special'] == special

    assert 'selected_date' in response.context
    assert response.context['selected_date'] == localtime(event.event_date).date()

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
    from events.models import Event
    from events.tests.factories import EventFactory
    from specials.tests.factories import SpecialFactory

    matching = EventFactory(target_audience=Event.TargetAudience.PROFESSIONALS)
    other = EventFactory(target_audience=Event.TargetAudience.FAMILIES)
    special = SpecialFactory(related_events=[matching, other])

    response = django_app.get(
        reverse('specials:special_detail', args=[special.slug]),
        {
            'target_audience': 'professionals',
            'fecha': str(localtime(matching.event_date).date()),
        },
        status=200,
    )
    assert matching in response.context['events']
    assert other not in response.context['events']


@pytest.mark.django_db
def test_filter_events_by_target_audience_stacks_with_date(django_app):
    from datetime import timedelta

    from django.utils.timezone import now

    from events.models import Event
    from events.tests.factories import EventFactory
    from specials.tests.factories import SpecialFactory

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
            'target_audience': 'children',
            'fecha': str(localtime(target_date).date()),
        },
        status=200,
    )
    assert matching in response.context['events']
    assert wrong_audience not in response.context['events']
    assert wrong_date not in response.context['events']
