import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'dashboard_view_name',
    [
        'dashboard:home',
        'dashboard:social_posts',
        'dashboard:users',
        'dashboard:places',
        'dashboard:filbo_event_form',
        'dashboard:spreadsheet_sync_form',
    ],
)
def test_access_denied_for_non_admin_users(django_app, user, dashboard_view_name):
    django_app.get(reverse(dashboard_view_name), user=user, status=403)
