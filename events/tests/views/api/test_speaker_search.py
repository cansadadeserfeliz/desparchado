import pytest
from django.urls import reverse
from rest_framework import status

from events.tests.factories import SpeakerFactory
from users.tests.factories import UserFactory

SEARCH_URL = 'events_api:speaker_search'


@pytest.mark.django_db
def test_unauthenticated_request_returns_403(client):
    response = client.get(reverse(SEARCH_URL), {'q': 'test'})
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_short_query_returns_empty_results(client):
    user = UserFactory()
    SpeakerFactory(name='Test Speaker')
    client.force_login(user)

    response = client.get(reverse(SEARCH_URL), {'q': 't'})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'results': []}


@pytest.mark.django_db
def test_absent_query_returns_first_items(client):
    user = UserFactory()
    SpeakerFactory(name='Test Speaker')
    client.force_login(user)

    response = client.get(reverse(SEARCH_URL))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['results']) == 1


@pytest.mark.django_db
def test_valid_query_returns_matching_results(client):
    user = UserFactory()
    SpeakerFactory(name='José García')
    SpeakerFactory(name='Ana Martínez')
    client.force_login(user)

    response = client.get(reverse(SEARCH_URL), {'q': 'garcia'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data['results']) == 1
    assert data['results'][0]['name'] == 'José García'


@pytest.mark.django_db
def test_response_shape_contains_id_and_name(client):
    user = UserFactory()
    speaker = SpeakerFactory(name='María López')
    client.force_login(user)

    response = client.get(reverse(SEARCH_URL), {'q': 'maria'})
    assert response.status_code == status.HTTP_200_OK
    result = response.json()['results'][0]
    assert set(result.keys()) == {'id', 'name', 'image_url'}
    assert result['id'] == speaker.pk
    assert result['name'] == 'María López'


@pytest.mark.django_db
def test_accent_normalization_via_endpoint(client):
    user = UserFactory()
    SpeakerFactory(name='José García')
    client.force_login(user)

    response = client.get(reverse(SEARCH_URL), {'q': 'jose garcia'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data['results']) == 1
    assert data['results'][0]['name'] == 'José García'
