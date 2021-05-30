import pytest

from django.urls import reverse


@pytest.mark.django_db
def test_show_events_list(django_app, user_admin, history_event):
    response = django_app.get(
        reverse('admin:history_event_changelist'),
        user=user_admin,
        status=200
    )
    assert history_event.title in response
