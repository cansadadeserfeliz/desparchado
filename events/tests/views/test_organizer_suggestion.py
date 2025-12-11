import pytest
from django.urls import reverse
from rest_framework import status

from events.tests.factories import OrganizerFactory


@pytest.mark.django_db
def test_successfully_get_organizer_suggestion(client, user):
    client.force_login(user)
    organizer = OrganizerFactory(name='Museo Nacional')

    response = client.get(
        reverse('events:organizer_suggestions'),
        {'query': organizer.name},
    )
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()

    assert 'suggestion' in response_json
    suggestion = response_json['suggestion']
    assert 'Advertencia para evitar agregar organizadores duplicados' in suggestion
    assert organizer.name in suggestion


@pytest.mark.django_db
def test_non_authenticated_user_cannot_get_organizer_suggestion(client):
    organizer = OrganizerFactory(name='Museo Nacional')
    response = client.get(
        reverse('events:organizer_suggestions'),
        {'query': organizer.name},
    )
    assert response.status_code == status.HTTP_302_FOUND
