import pytest
from django.urls import reverse

from events.views.event_wizard_create import QUOTA_EXCEEDED_MESSAGE
from users.tests.factories import UserFactory

VIEW_NAME = 'events:add_event'


@pytest.mark.django_db
def test_redirects_unauthenticated_user_to_login(django_app) -> None:
    """Unauthenticated GET to the wizard redirects to login with a next param.

    Args:
        django_app: WebTest client fixture.

    Returns:
        None
    """
    response = django_app.get(reverse(VIEW_NAME), status=302)
    assert reverse('account_login') in response.location
    assert f'next={reverse(VIEW_NAME)}' in response.location


@pytest.mark.django_db
def test_quota_exceeded_returns_403(django_app) -> None:
    """Authenticated user who has exhausted their daily quota receives a 403.

    Args:
        django_app: WebTest client fixture.

    Returns:
        None
    """
    user = UserFactory()
    user.settings.event_creation_quota = 0
    user.settings.save()

    response = django_app.get(reverse(VIEW_NAME), user=user, status=403)
    assert QUOTA_EXCEEDED_MESSAGE in response.text
    assert any('403.html' in t.name for t in response.templates)


@pytest.mark.django_db
def test_within_quota_returns_200_with_wizard_template(django_app) -> None:
    """Authenticated user within quota receives a 200 with the wizard template.

    Args:
        django_app: WebTest client fixture.

    Returns:
        None
    """
    user = UserFactory()
    response = django_app.get(reverse(VIEW_NAME), user=user, status=200)
    assert any(t.name == 'events/event_wizard.html' for t in response.templates)


@pytest.mark.django_db
def test_wizard_template_contains_mount_element(django_app) -> None:
    """Wizard template contains the Vue mount element with required data attributes.

    Args:
        django_app: WebTest client fixture.

    Returns:
        None
    """
    user = UserFactory()
    response = django_app.get(reverse(VIEW_NAME), user=user, status=200)

    assert 'data-vue-component="event-wizard"' in response.text
    assert 'data-wizard-mode="create"' in response.text
    assert 'data-csrf=' in response.text
    assert 'data-api-url=' in response.text


@pytest.mark.django_db
def test_superuser_bypasses_quota(django_app) -> None:
    """Superuser with zero quota still accesses the wizard.

    Args:
        django_app: WebTest client fixture.

    Returns:
        None
    """
    superuser = UserFactory(is_superuser=True)
    superuser.settings.event_creation_quota = 0
    superuser.settings.save()

    response = django_app.get(reverse(VIEW_NAME), user=superuser, status=200)
    assert any(t.name == 'events/event_wizard.html' for t in response.templates)
