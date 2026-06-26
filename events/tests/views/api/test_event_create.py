import io
from unittest.mock import patch

import pytest
from django.urls import reverse
from PIL import Image
from rest_framework import status

from events.models import Event
from events.tests.factories import OrganizerFactory
from places.tests.factories import PlaceFactory
from users.tests.factories import UserFactory


def _make_image_file(filename: str = 'test.jpg') -> io.BytesIO:
    img = Image.new('RGB', (10, 10), color='red')
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.name = filename
    buf.seek(0)
    return buf


def _valid_payload(place, organizer) -> dict:
    return {
        'title': 'Mi evento de prueba',
        'description': '<p>Descripción del evento</p>',
        'event_source_url': 'https://example.com/evento',
        'event_date': '2030-12-01T18:00:00-05:00',
        'place_id': place.pk,
        'organizer_ids': [organizer.pk],
    }


CREATE_URL = 'events_api:event_create'


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_unauthenticated_post_is_rejected(client):
    """SessionAuthentication returns 403 (no WWW-Authenticate header)
    for anonymous users."""
    place = PlaceFactory()
    organizer = OrganizerFactory()
    response = client.post(
        reverse(CREATE_URL),
        data=_valid_payload(place, organizer),
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# Successful creation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_valid_post_creates_event_and_returns_201(client):
    user = UserFactory()
    place = PlaceFactory()
    organizer = OrganizerFactory()
    client.force_login(user)

    with patch('events.views.api.event_create.send_notification') as mock_notify:
        response = client.post(
            reverse(CREATE_URL),
            data=_valid_payload(place, organizer),
        )

    assert response.status_code == status.HTTP_201_CREATED
    assert 'url' in response.json()

    event = Event.objects.get(title='Mi evento de prueba')
    assert event.created_by == user
    assert event.is_approved is True
    assert event.organizers.filter(pk=organizer.pk).exists()
    mock_notify.assert_called_once()


@pytest.mark.django_db
def test_valid_post_response_url_matches_event(client):
    user = UserFactory()
    place = PlaceFactory()
    organizer = OrganizerFactory()
    client.force_login(user)

    with patch('events.views.api.event_create.send_notification'):
        response = client.post(
            reverse(CREATE_URL),
            data=_valid_payload(place, organizer),
        )

    event = Event.objects.get(title='Mi evento de prueba')
    assert event.get_absolute_url() in response.json()['url']


@pytest.mark.django_db
def test_valid_post_with_image_stores_image(client):
    user = UserFactory()
    place = PlaceFactory()
    organizer = OrganizerFactory()
    client.force_login(user)

    payload = _valid_payload(place, organizer)
    payload['image'] = _make_image_file()

    with patch('events.views.api.event_create.send_notification'):
        response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_201_CREATED
    event = Event.objects.get(title='Mi evento de prueba')
    assert bool(event.image)


# ---------------------------------------------------------------------------
# Required-field validation → 400
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.parametrize('missing_field', [
    'title',
    'description',
    'event_source_url',
    'event_date',
    'place_id',
    'organizer_ids',
])
def test_missing_required_field_returns_400(client, missing_field):
    user = UserFactory()
    place = PlaceFactory()
    organizer = OrganizerFactory()
    client.force_login(user)

    payload = _valid_payload(place, organizer)
    del payload[missing_field]

    with patch('events.views.api.event_create.send_notification'):
        response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert missing_field in response.json()


@pytest.mark.django_db
def test_empty_organizer_ids_returns_400(client):
    user = UserFactory()
    place = PlaceFactory()
    client.force_login(user)

    payload = {
        'title': 'Test',
        'description': 'Descripción',
        'event_source_url': 'https://example.com',
        'event_date': '2030-12-01T18:00:00-05:00',
        'place_id': place.pk,
    }

    with patch('events.views.api.event_create.send_notification'):
        response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'organizer_ids' in response.json()


# ---------------------------------------------------------------------------
# FK validation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_nonexistent_place_id_returns_400(client):
    user = UserFactory()
    organizer = OrganizerFactory()
    client.force_login(user)

    payload = {
        'title': 'Test',
        'description': 'Descripción',
        'event_source_url': 'https://example.com',
        'event_date': '2030-12-01T18:00:00-05:00',
        'place_id': 999999,
        'organizer_ids': [organizer.pk],
    }

    with patch('events.views.api.event_create.send_notification'):
        response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'place_id' in response.json()


@pytest.mark.django_db
def test_nonexistent_organizer_id_returns_400(client):
    user = UserFactory()
    place = PlaceFactory()
    client.force_login(user)

    payload = {
        'title': 'Test',
        'description': 'Descripción',
        'event_source_url': 'https://example.com',
        'event_date': '2030-12-01T18:00:00-05:00',
        'place_id': place.pk,
        'organizer_ids': [999999],
    }

    with patch('events.views.api.event_create.send_notification'):
        response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'organizer_ids' in response.json()


# ---------------------------------------------------------------------------

# Reserved-slug avoidance
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.parametrize('reserved_title', ['Create', 'Future'])
def test_post_with_reserved_title_generates_safe_slug(client, reserved_title):
    user = UserFactory()
    place = PlaceFactory()
    organizer = OrganizerFactory()
    client.force_login(user)

    payload = _valid_payload(place, organizer)
    payload['title'] = reserved_title

    with patch('events.views.api.event_create.send_notification'):
        response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_201_CREATED
    from events.models.event import RESERVED_EVENT_SLUGS
    event = Event.objects.get(title=reserved_title)
    assert event.slug not in RESERVED_EVENT_SLUGS


# ---------------------------------------------------------------------------
# HTML sanitization
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_script_tag_in_description_is_sanitized(client):
    user = UserFactory()
    place = PlaceFactory()
    organizer = OrganizerFactory()
    client.force_login(user)

    payload = _valid_payload(place, organizer)
    payload['description'] = '<p>Hola</p><script>alert("xss")</script>'
    payload['title'] = 'Evento sanitización'

    with patch('events.views.api.event_create.send_notification'):
        response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_201_CREATED
    event = Event.objects.get(title='Evento sanitización')
    assert '<script>' not in event.description
    assert 'Hola' in event.description


# ---------------------------------------------------------------------------
# Quota enforcement
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_quota_exceeded_returns_403(client, user_with_zero_event_quota):
    client.force_login(user_with_zero_event_quota)

    place = PlaceFactory()
    organizer = OrganizerFactory()
    response = client.post(reverse(CREATE_URL), data=_valid_payload(place, organizer))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()['detail'] == (
        'Hoy alcanzaste el límite de eventos que puedes crear. '
        'Vuelve mañana para continuar publicando.'
    )


@pytest.mark.django_db
def test_superuser_bypasses_quota(client, user_admin):
    user_admin.settings.event_creation_quota = 0
    user_admin.settings.save()
    client.force_login(user_admin)

    place = PlaceFactory()
    organizer = OrganizerFactory()
    with patch('events.views.api.event_create.send_notification'):
        response = client.post(
            reverse(CREATE_URL), data=_valid_payload(place, organizer),
        )

    assert response.status_code == status.HTTP_201_CREATED
