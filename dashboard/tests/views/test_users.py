import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_places(client, admin_user, user):
    client.force_login(admin_user)
    response = client.get(reverse('dashboard:users'))
    assert response.status_code == status.HTTP_200_OK

    assert 'recently_registered_users' in response.context
    assert 'users_with_most_events' in response.context
    assert 'duplicated_emails' in response.context

    assert user in response.context['recently_registered_users']
