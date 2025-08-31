import pytest
from django.urls import reverse

VIEW_NAME = 'events:event_detail'


@pytest.mark.django_db
def test_show_details_of_not_published_event(django_app, not_published_event):
    django_app.get(
        reverse(VIEW_NAME, args=[not_published_event.slug]),
        status=404,
    )


@pytest.mark.django_db
def test_show_details_of_not_approved_event(django_app, not_approved_event):
    django_app.get(
        reverse(VIEW_NAME, args=[not_approved_event.slug]), status=404,
    )


@pytest.mark.django_db
def test_show_details_of_event(django_app, event):
    response = django_app.get(
        reverse(VIEW_NAME, args=[event.slug]), status=200,
    )
    assert event == response.context['event']
