import pytest
from django.urls import reverse
from rest_framework import status

from events.tests.factories import OrganizerFactory


@pytest.mark.django_db
def test_successfully_get_organizer_via_autocomplete(client, user):
    client.force_login(user)

    organizer = OrganizerFactory(name='BLAA')
    # Create an organizer that won't appear in search results
    OrganizerFactory(name='Museo Nacional')

    response = client.get(
        reverse('events:organizer_autocomplete'),
        {'q': organizer.name},
    )
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()

    assert 'results' in response_json
    results = response_json['results']
    assert len(results) == 1
    assert results[0]['id'] == str(organizer.id)
    assert results[0]['selected_text'] == organizer.name


@pytest.mark.django_db
def test_non_authenticated_user_cannot_get_organizer_via_autocomplete(client):
    organizer = OrganizerFactory(name='BLAA')
    response = client.get(
        reverse('events:organizer_autocomplete'),
        {'q': organizer.name},
    )
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()

    assert 'results' in response_json
    assert len(response_json['results']) == 0
