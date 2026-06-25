import pytest
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from django.urls import reverse
from rest_framework import status

from events.tests.factories import EventFactory, OrganizerFactory
from places.tests.factories import PlaceFactory
from users.tests.factories import UserFactory

UPDATE_URL = 'events_api:event_update'


def _patch(client, slug: str, data: dict):
    return client.patch(
        reverse(UPDATE_URL, args=[slug]),
        data=encode_multipart(BOUNDARY, data),
        content_type=MULTIPART_CONTENT,
    )


# ---------------------------------------------------------------------------
# PATCH — success
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_patch_returns_200_and_event_url_for_creator(client):
    organizer = OrganizerFactory()
    event = EventFactory(organizers=[organizer])
    client.force_login(event.created_by)

    response = _patch(client, event.slug, {'title': 'Título actualizado'})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['url'] == event.get_absolute_url()


@pytest.mark.django_db
def test_patch_updates_event_in_db(client):
    organizer = OrganizerFactory()
    event = EventFactory(organizers=[organizer])
    client.force_login(event.created_by)

    _patch(client, event.slug, {'title': 'Nuevo título'})

    event.refresh_from_db()
    assert event.title == 'Nuevo título'


@pytest.mark.django_db
def test_patch_allows_partial_update(client):
    organizer = OrganizerFactory()
    place = PlaceFactory()
    event = EventFactory(organizers=[organizer], place=place)
    original_place_id = event.place_id
    client.force_login(event.created_by)

    _patch(client, event.slug, {'title': 'Solo el título cambia'})

    event.refresh_from_db()
    assert event.title == 'Solo el título cambia'
    assert event.place_id == original_place_id
    assert event.organizers.filter(pk=organizer.pk).exists()


@pytest.mark.django_db
def test_superuser_can_patch_any_event(client):
    organizer = OrganizerFactory()
    event = EventFactory(organizers=[organizer])
    superuser = UserFactory(is_superuser=True, is_staff=True)
    client.force_login(superuser)

    response = _patch(client, event.slug, {'title': 'Editado por superusuario'})

    assert response.status_code == status.HTTP_200_OK


# ---------------------------------------------------------------------------
# PATCH — permission failures
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_patch_returns_403_for_non_editor(client):
    organizer = OrganizerFactory()
    event = EventFactory(organizers=[organizer])
    other_user = UserFactory()
    client.force_login(other_user)

    response = _patch(client, event.slug, {'title': 'Intento no autorizado'})

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_patch_returns_403_for_unauthenticated_user(client):
    organizer = OrganizerFactory()
    event = EventFactory(organizers=[organizer])

    response = _patch(client, event.slug, {'title': 'Sin autenticación'})

    assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# PATCH — validation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_patch_sanitizes_description_html(client):
    organizer = OrganizerFactory()
    event = EventFactory(organizers=[organizer])
    client.force_login(event.created_by)

    dirty_html = '<p>Texto seguro</p><script>alert("xss")</script>'
    response = _patch(client, event.slug, {'description': dirty_html})

    assert response.status_code == status.HTTP_200_OK
    event.refresh_from_db()
    assert '<script>' not in event.description
    assert 'Texto seguro' in event.description


@pytest.mark.django_db
def test_patch_returns_400_for_invalid_data(client):
    organizer = OrganizerFactory()
    event = EventFactory(organizers=[organizer])
    client.force_login(event.created_by)

    response = _patch(client, event.slug, {'event_source_url': 'no-es-una-url'})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'event_source_url' in response.json()
