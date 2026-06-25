import pytest
from django.urls import NoReverseMatch, reverse
from rest_framework import status

from events.views.event_wizard_update import EDIT_DENIED_MESSAGE

VIEW_NAME = 'events:event_wizard_update'


@pytest.mark.django_db
def test_edit_unauthenticated_redirects_to_login(django_app, event) -> None:
    edit_url = reverse(VIEW_NAME, args=[event.slug])

    response = django_app.get(edit_url, status=status.HTTP_302_FOUND)

    assert reverse('account_login') in response.location
    assert f'next={edit_url}' in response.location


@pytest.mark.django_db
def test_edit_non_editor_receives_403(django_app, event, other_user) -> None:
    django_app.get(
        reverse(VIEW_NAME, args=[event.slug]),
        user=other_user,
        status=status.HTTP_403_FORBIDDEN,
    )


@pytest.mark.django_db
def test_edit_403_contains_permission_message(django_app, event, other_user) -> None:
    response = django_app.get(
        reverse(VIEW_NAME, args=[event.slug]),
        user=other_user,
        status=status.HTTP_403_FORBIDDEN,
    )

    assert EDIT_DENIED_MESSAGE in response.text
    assert any('403.html' in t.name for t in response.templates)


@pytest.mark.django_db
def test_edit_authorized_creator_receives_200(django_app, event) -> None:
    response = django_app.get(
        reverse(VIEW_NAME, args=[event.slug]),
        user=event.created_by,
        status=status.HTTP_200_OK,
    )

    assert any(t.name == 'events/event_wizard.html' for t in response.templates)


@pytest.mark.django_db
def test_edit_wizard_template_contains_mount_attributes(django_app, event) -> None:
    response = django_app.get(
        reverse(VIEW_NAME, args=[event.slug]),
        user=event.created_by,
        status=status.HTTP_200_OK,
    )

    assert 'data-vue-component="event-wizard"' in response.text
    assert 'data-wizard-mode="edit"' in response.text
    assert 'data-csrf=' in response.text
    expected_api_url = reverse('events_api:event_detail', args=[event.slug])
    assert f'data-api-url="{expected_api_url}"' in response.text
    expected_api_update_url = reverse('events_api:event_update', args=[event.slug])
    assert f'data-api-update-url="{expected_api_update_url}"' in response.text


@pytest.mark.django_db
def test_edit_superuser_can_edit_any_event(django_app, event, user_admin) -> None:
    response = django_app.get(
        reverse(VIEW_NAME, args=[event.slug]),
        user=user_admin,
        status=status.HTTP_200_OK,
    )

    assert any(t.name == 'events/event_wizard.html' for t in response.templates)


@pytest.mark.django_db
def test_edit_nonexistent_event_returns_404(django_app, user) -> None:
    django_app.get(
        reverse(VIEW_NAME, args=['nonexistent-slug']),
        user=user,
        status=status.HTTP_404_NOT_FOUND,
    )


def test_old_event_update_url_no_longer_resolves() -> None:
    with pytest.raises(NoReverseMatch):
        reverse('events:event_update', args=[1])
