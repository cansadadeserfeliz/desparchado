import pytest

from django.urls import reverse
from users.tests.factories import UserFactory


@pytest.fixture
def user():
    return UserFactory(
        is_superuser=False,
        is_staff=False,
        is_active=True,
    )


@pytest.mark.django_db
def test_home_view(django_app, admin_user):
    response = django_app.get(
        reverse('dashboard:home'),
        user=admin_user,
        status=200
    )
    assert 'future_events_count' in response.context


@pytest.mark.django_db
def test_access_denied_for_non_admin_users(django_app, user):
    django_app.get(
        reverse('dashboard:home'),
        user=user,
        status=403
    )
