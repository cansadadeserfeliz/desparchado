import pytest
from django.urls import reverse

from events.views.event_wizard_create import QUOTA_EXCEEDED_MESSAGE
from users.tests.factories import UserFactory

VIEW_NAME = 'events:add_event'


@pytest.mark.django_db
def test_redirects_unauthenticated_user_to_login(django_app):
    response = django_app.get(reverse(VIEW_NAME), status=302)
    assert reverse('account_login') in response.location
    assert f'next={reverse(VIEW_NAME)}' in response.location


@pytest.mark.django_db
def test_quota_exceeded_returns_403(django_app):
    user = UserFactory()
    user.settings.event_creation_quota = 0
    user.settings.save()

    response = django_app.get(reverse(VIEW_NAME), user=user, status=403)
    assert QUOTA_EXCEEDED_MESSAGE in response.text
    assert any('403.html' in t.name for t in response.templates)


@pytest.mark.django_db
def test_within_quota_returns_200_with_wizard_template(django_app):
    user = UserFactory()
    response = django_app.get(reverse(VIEW_NAME), user=user, status=200)
    assert any(t.name == 'events/event_wizard.html' for t in response.templates)


@pytest.mark.django_db
def test_wizard_template_contains_mount_element(django_app):
    user = UserFactory()
    response = django_app.get(reverse(VIEW_NAME), user=user, status=200)

    assert 'id="event-wizard-app"' in response.text
    assert 'data-wizard-mode="create"' in response.text
    assert 'data-csrf=' in response.text
    assert 'data-api-url=' in response.text


@pytest.mark.django_db
def test_superuser_bypasses_quota(django_app):
    superuser = UserFactory(is_superuser=True)
    superuser.settings.event_creation_quota = 0
    superuser.settings.save()

    django_app.get(reverse(VIEW_NAME), user=superuser, status=200)
