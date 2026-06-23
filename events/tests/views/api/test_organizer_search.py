import pytest
from django.urls import reverse
from rest_framework import status

from events.tests.factories import OrganizerFactory
from users.tests.factories import UserFactory

SEARCH_URL = 'events_api:organizer_search'


@pytest.mark.django_db
def test_unauthenticated_request_returns_403(client):
    response = client.get(reverse(SEARCH_URL), {'q': 'test'})
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_short_query_returns_empty_results(client):
    user = UserFactory()
    OrganizerFactory(name='Test Organizer')
    client.force_login(user)

    response = client.get(reverse(SEARCH_URL), {'q': 't'})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'results': []}


@pytest.mark.django_db
def test_absent_query_returns_first_items(client):
    user = UserFactory()
    OrganizerFactory(name='Test Organizer')
    client.force_login(user)

    response = client.get(reverse(SEARCH_URL))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['results']) == 1


@pytest.mark.django_db
def test_valid_query_returns_matching_results(client):
    user = UserFactory()
    OrganizerFactory(name='Feria Internacional del Libro')
    OrganizerFactory(name='Museo Nacional')
    client.force_login(user)

    response = client.get(reverse(SEARCH_URL), {'q': 'feria'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'results' in data
    assert len(data['results']) == 1
    assert data['results'][0]['name'] == 'Feria Internacional del Libro'


@pytest.mark.django_db
def test_response_shape_contains_id_and_name(client):
    user = UserFactory()
    organizer = OrganizerFactory(name='Planeta Educación')
    client.force_login(user)

    response = client.get(reverse(SEARCH_URL), {'q': 'planeta'})
    assert response.status_code == status.HTTP_200_OK
    result = response.json()['results'][0]
    assert set(result.keys()) == {'id', 'name', 'image_url'}
    assert result['id'] == organizer.pk
    assert result['name'] == 'Planeta Educación'


@pytest.mark.django_db
def test_accent_normalization_via_endpoint(client):
    user = UserFactory()
    OrganizerFactory(name='Biblioteca Luis Ángel Arango')
    client.force_login(user)

    response = client.get(reverse(SEARCH_URL), {'q': 'luis angel arango'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data['results']) == 1
    assert data['results'][0]['name'] == 'Biblioteca Luis Ángel Arango'
