import pytest

from django.urls import reverse


@pytest.mark.django_db
def test_home_view(django_app, admin_user):
    response = django_app.get(
        reverse('dashboard:home'),
        user=admin_user,
        status=200
    )
    assert 'future_events_count' in response.context


@pytest.mark.django_db
@pytest.mark.parametrize('dashboard_view_name', [
    'dashboard:home',
    'dashboard:events',
    'dashboard:social_posts',
    'dashboard:event_sources',
])
def test_access_denied_for_non_admin_users(django_app, user, dashboard_view_name):
    django_app.get(
        reverse(dashboard_view_name),
        user=user,
        status=403
    )
