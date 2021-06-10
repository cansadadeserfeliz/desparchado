import pytest

from django.urls import reverse

from events.tests.factories import EventFactory
from .factories import UserFactory


@pytest.mark.django_db
def test_successfully_shows_user_detail(django_app, user):
    response = django_app.get(
        reverse('users:user_detail', args=[user.username]),
        status=200
    )
    assert response.context['user_object'] == user
    assert user.first_name in response


@pytest.mark.django_db
def test_successfully_shows_user_detail_for_authenticated_user(django_app, user):
    response = django_app.get(
        reverse('users:user_detail', args=[user.username]),
        user=user,
        status=200
    )
    assert response.context['user_object'] == user
    assert user.first_name in response


@pytest.mark.django_db
def test_user_added_events_list_redirects_for_non_authenticated_user(django_app):
    response = django_app.get(
        reverse('users:user_added_events_list'),
        status=302
    )
    assert reverse('users:login') in response.location


@pytest.mark.django_db
def test_successfully_shows_user_events(django_app, user, other_user):
    first_event = EventFactory(created_by=user)
    second_event = EventFactory(created_by=user)

    other_user_event = EventFactory(
        created_by=other_user
    )

    response = django_app.get(
        reverse('users:user_added_events_list'),
        user=user,
        status=200
    )

    assert user == response.context['user_object']
    assert len(response.context['events']) == 2
    assert first_event in response.context['events']
    assert second_event in response.context['events']
    assert other_user_event not in response.context['events']
