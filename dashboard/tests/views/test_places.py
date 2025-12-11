import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_places(client, admin_user, place):
    client.force_login(admin_user)
    response = client.get(reverse('dashboard:places'))
    assert response.status_code == status.HTTP_200_OK

    assert 'places' in response.context
    assert place in response.context['places']
