import pytest

from django.utils.timezone import localtime
from django.urls import reverse


@pytest.mark.django_db
def test_successfully_show_special(django_app, special, event):
    assert special.related_events.count() == 3

    response = django_app.get(
        reverse('specials:special_detail', args=[special.slug]),
        status=200
    )
    assert response.context['special'] == special

    assert 'selected_date' in response.context
    assert response.context['selected_date'] == localtime(event.event_date).date()

    assert 'events' in response.context
    assert event in response.context['events']
    assert len(response.context['events']) == 1, 'only published event should be returned'


@pytest.mark.django_db
def test_does_not_show_not_published_special(django_app, special):
    special.is_published = False
    special.save()

    django_app.get(
        reverse('specials:special_detail', args=[special.slug]),
        status=404
    )
