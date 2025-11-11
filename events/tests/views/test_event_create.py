from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from events.models import Event

VIEW_NAME = 'events:add_event'


@pytest.mark.django_db
def test_redirects_for_anonymous_user(django_app):
    response = django_app.get(reverse(VIEW_NAME), status=302)
    assert reverse('account_login') in response.location


@pytest.mark.django_db
def test_successfully_create_event(django_app, user, organizer, place):
    events_count = Event.objects.count()
    response = django_app.get(reverse(VIEW_NAME), user=user, status=200)

    form = response.forms['event_form']
    form['title'] = 'Presentación del libro de Julian Barnes'
    form['description'] = (
        'Hasta hace poco he visto a Julian Barnes '
        'como uno de esos escritores que nos interesan, '
        'cuya lectura creemos inminente, '
        'pero que vamos aplazando año tras año '
        'sin ningún motivo concreto.'
    )
    form['category'] = Event.Category.LITERATURE
    form['event_date'] = (timezone.now() + timedelta(days=1)).strftime('%d/%m/%Y %H:%M')
    form['event_source_url'] = 'https://example.com'
    form['organizers'].force_value([organizer.id])
    form['place'].force_value(place.id)

    response = form.submit()
    assert response.status_code == 302

    assert Event.objects.count() == events_count + 1
    event = Event.objects.first()
    assert event.created_by == user
    assert event.category == Event.Category.LITERATURE

    assert event.get_absolute_url() in response.location
