import pytest
from django.urls import reverse
from rest_framework import status

from users.tests.factories import UserFactory


@pytest.mark.django_db
def test_unauthenticated_user(client):
    response = client.get(reverse('playground:home'))
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_regular_user(client):
    client.force_login(UserFactory(is_superuser=False))
    response = client.get(reverse('playground:home'))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_successfully_show_home_page(client, user_admin):
    client.force_login(user_admin)
    response = client.get(reverse('playground:home'))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_successfully_show_event_page(client, user_admin, event):
    client.force_login(user_admin)
    response = client.get(reverse('playground:event_detail'))
    assert response.status_code == status.HTTP_200_OK
