import pytest
from django.urls import reverse
from rest_framework import status

from places.tests.factories import PlaceFactory
from users.tests.factories import UserFactory

SEARCH_URL = 'places_api:place_search'


@pytest.mark.django_db
def test_unauthenticated_request_returns_403(client):
    response = client.get(reverse(SEARCH_URL), {'q': 'test'})
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_short_query_returns_empty_results(client):
    user = UserFactory()
    PlaceFactory(name='Test Place')
    client.force_login(user)

    response = client.get(reverse(SEARCH_URL), {'q': 't'})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'results': []}


@pytest.mark.django_db
def test_absent_query_returns_first_items(client):
    user = UserFactory()
    PlaceFactory(name='Test Place')
    client.force_login(user)

    response = client.get(reverse(SEARCH_URL))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['results']) == 1


@pytest.mark.django_db
def test_valid_query_returns_matching_results(client):
    user = UserFactory()
    PlaceFactory(name='Jardín Botánico de Bogotá')
    PlaceFactory(name='Museo del Oro')
    client.force_login(user)

    response = client.get(reverse(SEARCH_URL), {'q': 'jardin'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data['results']) == 1
    assert data['results'][0]['name'] == 'Jardín Botánico de Bogotá'


@pytest.mark.django_db
def test_response_shape_contains_id_and_name(client):
    user = UserFactory()
    place = PlaceFactory(name='Teatro Colón')
    client.force_login(user)

    response = client.get(reverse(SEARCH_URL), {'q': 'teatro colon'})
    assert response.status_code == status.HTTP_200_OK
    result = response.json()['results'][0]
    assert set(result.keys()) == {'id', 'name'}
    assert result['id'] == place.pk
    assert result['name'] == 'Teatro Colón'


@pytest.mark.django_db
def test_accent_normalization_via_endpoint(client):
    user = UserFactory()
    PlaceFactory(name='Jardín Botánico de Bogotá')
    client.force_login(user)

    response = client.get(reverse(SEARCH_URL), {'q': 'jardin botanico'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data['results']) == 1
    assert data['results'][0]['name'] == 'Jardín Botánico de Bogotá'
