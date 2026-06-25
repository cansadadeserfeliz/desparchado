import pytest
from django.urls import reverse
from rest_framework import status

from events.tests.factories import EventFactory, OrganizerFactory, SpeakerFactory
from users.tests.factories import UserFactory

DETAIL_URL = 'events_api:event_detail'


def _url(slug: str) -> str:
    return reverse(DETAIL_URL, args=[slug])


# ---------------------------------------------------------------------------
# GET — field coverage
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_returns_200_with_event_fields(client):
    organizer = OrganizerFactory()
    event = EventFactory(organizers=[organizer])
    client.force_login(event.created_by)

    response = client.get(_url(event.slug))

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['title'] == event.title
    assert data['description'] == event.description
    assert 'image_url' in data
    assert 'event_date' in data
    assert data['category'] == event.category
    assert 'price' in data
    assert data['event_source_url'] == event.event_source_url
    assert data['is_published'] == event.is_published


@pytest.mark.django_db
def test_get_returns_403_for_unauthenticated_user(client):
    event = EventFactory()
    response = client.get(_url(event.slug))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_returns_403_for_non_editor(client):
    event = EventFactory()
    other_user = UserFactory()
    client.force_login(other_user)
    response = client.get(_url(event.slug))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_returns_404_for_nonexistent_slug(client):
    user = UserFactory()
    client.force_login(user)
    response = client.get(_url('no-such-slug'))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_includes_organizers_with_id_name_and_image_url(client):
    organizer = OrganizerFactory()
    event = EventFactory(organizers=[organizer])
    client.force_login(event.created_by)

    response = client.get(_url(event.slug))

    organizers = response.json()['organizers']
    assert len(organizers) == 1
    assert organizers[0]['id'] == organizer.pk
    assert organizers[0]['name'] == organizer.name
    assert organizers[0]['image_url']


@pytest.mark.django_db
def test_get_includes_speakers_with_id_name_and_image_url(client):
    speaker = SpeakerFactory()
    organizer = OrganizerFactory()
    event = EventFactory(organizers=[organizer], speakers=[speaker])
    client.force_login(event.created_by)

    response = client.get(_url(event.slug))

    speakers = response.json()['speakers']
    assert len(speakers) == 1
    assert speakers[0]['id'] == speaker.pk
    assert speakers[0]['name'] == speaker.name
    assert speakers[0]['image_url']


@pytest.mark.django_db
def test_get_includes_place_with_city_id(client):
    organizer = OrganizerFactory()
    event = EventFactory(organizers=[organizer])
    client.force_login(event.created_by)

    response = client.get(_url(event.slug))

    place = response.json()['place']
    assert place['id'] == event.place.pk
    assert place['name'] == event.place.name
    assert place['city_id'] == event.place.city_id
