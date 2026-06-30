import pytest
from django.urls import reverse
from rest_framework import status

from events.permissions import QUOTA_EXCEEDED_MESSAGE

VIEW_NAME = 'events:event_wizard_create'


@pytest.mark.django_db
def test_redirects_unauthenticated_user_to_login(django_app) -> None:
    """Unauthenticated GET to the wizard redirects to login with a next param."""
    response = django_app.get(reverse(VIEW_NAME), status=status.HTTP_302_FOUND)
    assert reverse('account_login') in response.location
    assert f'next={reverse(VIEW_NAME)}' in response.location


@pytest.mark.django_db
def test_quota_exceeded_returns_403(django_app, user_with_zero_event_quota) -> None:
    """Authenticated user who has exhausted their daily quota receives a 403."""
    response = django_app.get(
        reverse(VIEW_NAME),
        user=user_with_zero_event_quota,
        status=status.HTTP_403_FORBIDDEN,
    )
    assert QUOTA_EXCEEDED_MESSAGE in response.text
    assert any('403.html' in t.name for t in response.templates)


@pytest.mark.django_db
def test_within_quota_returns_200_with_wizard_template(django_app, user) -> None:
    """Authenticated user within quota receives a 200 with the wizard template."""
    response = django_app.get(reverse(VIEW_NAME), user=user, status=status.HTTP_200_OK)
    assert any(t.name == 'events/event_wizard.html' for t in response.templates)


@pytest.mark.django_db
def test_wizard_template_contains_mount_element(django_app, user) -> None:
    """Wizard template contains the Vue mount element with required data attributes."""
    response = django_app.get(reverse(VIEW_NAME), user=user, status=status.HTTP_200_OK)

    assert 'data-vue-component="event-wizard"' in response.text
    assert 'data-wizard-mode="create"' in response.text
    assert 'data-api-url=' in response.text


@pytest.mark.django_db
def test_superuser_bypasses_quota(django_app, user_admin) -> None:
    """Superuser with zero quota still accesses the wizard."""
    user_admin.settings.event_creation_quota = 0
    user_admin.settings.save()

    response = django_app.get(
        reverse(VIEW_NAME), user=user_admin, status=status.HTTP_200_OK,
    )
    assert any(t.name == 'events/event_wizard.html' for t in response.templates)
