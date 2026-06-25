import io

import pytest
from django.urls import reverse
from PIL import Image
from rest_framework import status

from events.models import Speaker
from events.tests.factories import SpeakerFactory
from users.tests.factories import UserFactory

CREATE_URL = 'events_api:speaker_create'


def _make_image_file(filename: str = 'test.jpg') -> io.BytesIO:
    img = Image.new('RGB', (10, 10), color='green')
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.name = filename
    buf.seek(0)
    return buf


def _valid_payload() -> dict:
    return {
        'name': 'Ponente de Prueba',
        'description': '<p>Descripción del ponente</p>',
        'image': _make_image_file(),
        'image_source_url': 'https://example.com/image.jpg',
    }


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_unauthenticated_post_is_rejected(client):
    """SessionAuthentication returns 403 for anonymous users."""
    response = client.post(reverse(CREATE_URL), data=_valid_payload())
    assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# Successful creation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_valid_post_creates_speaker_and_returns_201(client):
    user = UserFactory()
    client.force_login(user)

    response = client.post(reverse(CREATE_URL), data=_valid_payload())

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert 'id' in data
    assert data['name'] == 'Ponente de Prueba'


@pytest.mark.django_db
def test_valid_post_sets_created_by(client):
    user = UserFactory()
    client.force_login(user)

    response = client.post(reverse(CREATE_URL), data=_valid_payload())

    assert response.status_code == status.HTTP_201_CREATED
    speaker = Speaker.objects.get(name='Ponente de Prueba')
    assert speaker.created_by == user


@pytest.mark.django_db
def test_valid_post_response_id_matches_created_speaker(client):
    user = UserFactory()
    client.force_login(user)

    response = client.post(reverse(CREATE_URL), data=_valid_payload())

    speaker = Speaker.objects.get(name='Ponente de Prueba')
    assert response.json()['id'] == speaker.pk


# ---------------------------------------------------------------------------
# Required-field validation → 400
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_missing_name_returns_400(client):
    user = UserFactory()
    client.force_login(user)

    payload = _valid_payload()
    del payload['name']
    response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'name' in response.json()


@pytest.mark.django_db
def test_duplicate_name_returns_400(client):
    user = UserFactory()
    client.force_login(user)
    SpeakerFactory(name='Ponente Duplicado')

    payload = _valid_payload()
    payload['name'] = 'Ponente Duplicado'
    response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'name' in response.json()


@pytest.mark.django_db
def test_missing_image_returns_400(client):
    user = UserFactory()
    client.force_login(user)

    payload = {
        'name': 'Ponente Sin Imagen',
        'description': '<p>Descripción</p>',
    }
    response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'image' in response.json()


# ---------------------------------------------------------------------------
# HTML sanitization
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_script_tag_in_description_is_sanitized(client):
    user = UserFactory()
    client.force_login(user)

    payload = _valid_payload()
    payload['name'] = 'Ponente Sanitización'
    payload['description'] = '<p>Hola</p><script>alert("xss")</script>'

    response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_201_CREATED
    speaker = Speaker.objects.get(name='Ponente Sanitización')
    assert '<script>' not in speaker.description
    assert 'Hola' in speaker.description


# ---------------------------------------------------------------------------
# Quota enforcement
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_quota_exceeded_returns_403(client, user_with_zero_speaker_quota):
    client.force_login(user_with_zero_speaker_quota)

    response = client.post(reverse(CREATE_URL), data=_valid_payload())

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()['detail'] == (
        'Hoy alcanzaste el límite de nuevos presentadores.'
    )


@pytest.mark.django_db
def test_superuser_bypasses_quota(client, user_admin):
    user_admin.settings.speaker_creation_quota = 0
    user_admin.settings.save()
    client.force_login(user_admin)

    response = client.post(reverse(CREATE_URL), data=_valid_payload())

    assert response.status_code == status.HTTP_201_CREATED
