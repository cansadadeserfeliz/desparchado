import pytest
from django.urls import reverse
from rest_framework import status

from events.tests.factories import SpeakerFactory


@pytest.mark.django_db
def test_successfully_get_speaker_via_autocomplete(client, user):
    client.force_login(user)

    speaker = SpeakerFactory(name='Jackson Lamb')
    # Create a speaker that won't appear in search results
    SpeakerFactory(name='River Cartwright')

    response = client.get(reverse('events:speaker_autocomplete'), {'q': speaker.name})
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()

    assert 'results' in response_json
    results = response_json['results']
    assert len(results) == 1
    assert results[0]['id'] == str(speaker.id)
    assert results[0]['selected_text'] == speaker.name


@pytest.mark.django_db
def test_non_authenticated_user_cannot_get_speaker_via_autocomplete(client):
    speaker = SpeakerFactory(name='Diana Taverner')
    response = client.get(reverse('events:speaker_autocomplete'), {'q': speaker.name})
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()

    assert 'results' in response_json
    assert len(response_json['results']) == 0
