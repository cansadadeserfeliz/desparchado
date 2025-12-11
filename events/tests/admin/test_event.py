import pytest
from django.urls import reverse
from rest_framework import status

from events.tests.factories import EventFactory


@pytest.mark.django_db
def test_successfully_get_admin_view(client, admin_user):
    client.force_login(admin_user)
    event = EventFactory()

    response = client.get(reverse('admin:events_event_changelist'))
    assert response.status_code == status.HTTP_200_OK
    assert event.title in response.text
