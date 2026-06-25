import pytest
from django.urls import NoReverseMatch, reverse

from events.tests.factories import EventFactory
from events.views.event_wizard_create import QUOTA_EXCEEDED_MESSAGE
from events.views.event_wizard_update import EDIT_DENIED_MESSAGE
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


EDIT_VIEW_NAME = 'events:event_wizard_update'


@pytest.mark.django_db
def test_edit_unauthenticated_redirects_to_login(django_app) -> None:
    event = EventFactory()
    edit_url = reverse(EDIT_VIEW_NAME, args=[event.slug])

    response = django_app.get(edit_url, status=302)

    assert reverse('account_login') in response.location
    assert f'next={edit_url}' in response.location


@pytest.mark.django_db
def test_edit_non_editor_receives_403(django_app) -> None:
    event = EventFactory()
    other_user = UserFactory()

    django_app.get(
        reverse(EDIT_VIEW_NAME, args=[event.slug]),
        user=other_user,
        status=403,
    )


@pytest.mark.django_db
def test_edit_403_contains_permission_message(django_app) -> None:
    event = EventFactory()
    other_user = UserFactory()

    response = django_app.get(
        reverse(EDIT_VIEW_NAME, args=[event.slug]),
        user=other_user,
        status=403,
    )

    assert EDIT_DENIED_MESSAGE in response.text
    assert any('403.html' in t.name for t in response.templates)


@pytest.mark.django_db
def test_edit_authorized_creator_receives_200(django_app) -> None:
    event = EventFactory()

    response = django_app.get(
        reverse(EDIT_VIEW_NAME, args=[event.slug]),
        user=event.created_by,
        status=200,
    )

    assert any(t.name == 'events/event_wizard.html' for t in response.templates)


@pytest.mark.django_db
def test_edit_wizard_template_contains_mount_attributes(django_app) -> None:
    event = EventFactory()

    response = django_app.get(
        reverse(EDIT_VIEW_NAME, args=[event.slug]),
        user=event.created_by,
        status=200,
    )

    assert 'data-vue-component="event-wizard"' in response.text
    assert 'data-wizard-mode="edit"' in response.text
    assert 'data-csrf=' in response.text
    assert f'data-api-url="/events/api/v1/events/{event.slug}/"' in response.text


@pytest.mark.django_db
def test_edit_superuser_can_edit_any_event(django_app) -> None:
    event = EventFactory()
    superuser = UserFactory(is_superuser=True)

    response = django_app.get(
        reverse(EDIT_VIEW_NAME, args=[event.slug]),
        user=superuser,
        status=200,
    )

    assert any(t.name == 'events/event_wizard.html' for t in response.templates)


@pytest.mark.django_db
def test_edit_nonexistent_event_returns_404(django_app) -> None:
    user = UserFactory()

    django_app.get(
        reverse(EDIT_VIEW_NAME, args=['nonexistent-slug']),
        user=user,
        status=404,
    )


def test_old_event_update_url_no_longer_resolves() -> None:
    with pytest.raises(NoReverseMatch):
        reverse('events:event_update', args=[1])
