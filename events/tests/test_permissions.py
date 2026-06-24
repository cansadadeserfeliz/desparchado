import pytest
from django.urls import reverse
from rest_framework import status

from users.tests.factories import UserFactory

EVENT_CREATE_URL = 'events_api:event_create'
ORGANIZER_CREATE_URL = 'events_api:organizer_create'
SPEAKER_CREATE_URL = 'events_api:speaker_create'
PLACE_CREATE_URL = 'places_api:place_create'


# ---------------------------------------------------------------------------
# EventCreationQuotaPermission
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_event_quota_permission_blocks_user_at_limit(client):
    user = UserFactory()
    user.settings.event_creation_quota = 0
    user.settings.save()
    client.force_login(user)

    response = client.post(reverse(EVENT_CREATE_URL), data={})

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_event_quota_permission_allows_user_under_limit(client):
    user = UserFactory()
    client.force_login(user)

    response = client.post(reverse(EVENT_CREATE_URL), data={})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_event_quota_permission_allows_superuser_at_limit(client):
    user = UserFactory(is_superuser=True)
    user.settings.event_creation_quota = 0
    user.settings.save()
    client.force_login(user)

    response = client.post(reverse(EVENT_CREATE_URL), data={})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_event_quota_permission_allows_safe_methods(client):
    user = UserFactory()
    user.settings.event_creation_quota = 0
    user.settings.save()
    client.force_login(user)

    response = client.get(reverse(EVENT_CREATE_URL))

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


# ---------------------------------------------------------------------------
# OrganizerCreationQuotaPermission
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_organizer_quota_permission_allows_safe_methods(client):
    user = UserFactory()
    user.settings.organizer_creation_quota = 0
    user.settings.save()
    client.force_login(user)

    response = client.get(reverse(ORGANIZER_CREATE_URL))

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_organizer_quota_permission_blocks_user_at_limit(client):
    user = UserFactory()
    user.settings.organizer_creation_quota = 0
    user.settings.save()
    client.force_login(user)

    response = client.post(reverse(ORGANIZER_CREATE_URL), data={})

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_organizer_quota_permission_allows_user_under_limit(client):
    user = UserFactory()
    client.force_login(user)

    response = client.post(reverse(ORGANIZER_CREATE_URL), data={})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_organizer_quota_permission_allows_superuser_at_limit(client):
    user = UserFactory(is_superuser=True)
    user.settings.organizer_creation_quota = 0
    user.settings.save()
    client.force_login(user)

    response = client.post(reverse(ORGANIZER_CREATE_URL), data={})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# SpeakerCreationQuotaPermission
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_speaker_quota_permission_allows_safe_methods(client):
    user = UserFactory()
    user.settings.speaker_creation_quota = 0
    user.settings.save()
    client.force_login(user)

    response = client.get(reverse(SPEAKER_CREATE_URL))

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_speaker_quota_permission_blocks_user_at_limit(client):
    user = UserFactory()
    user.settings.speaker_creation_quota = 0
    user.settings.save()
    client.force_login(user)

    response = client.post(reverse(SPEAKER_CREATE_URL), data={})

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_speaker_quota_permission_allows_user_under_limit(client):
    user = UserFactory()
    client.force_login(user)

    response = client.post(reverse(SPEAKER_CREATE_URL), data={})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_speaker_quota_permission_allows_superuser_at_limit(client):
    user = UserFactory(is_superuser=True)
    user.settings.speaker_creation_quota = 0
    user.settings.save()
    client.force_login(user)

    response = client.post(reverse(SPEAKER_CREATE_URL), data={})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# PlaceCreationQuotaPermission
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_place_quota_permission_allows_safe_methods(client):
    user = UserFactory()
    user.settings.place_creation_quota = 0
    user.settings.save()
    client.force_login(user)

    response = client.get(reverse(PLACE_CREATE_URL))

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_place_quota_permission_blocks_user_at_limit(client):
    user = UserFactory()
    user.settings.place_creation_quota = 0
    user.settings.save()
    client.force_login(user)

    response = client.post(reverse(PLACE_CREATE_URL), data={})

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_place_quota_permission_allows_user_under_limit(client):
    user = UserFactory()
    client.force_login(user)

    response = client.post(reverse(PLACE_CREATE_URL), data={})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_place_quota_permission_allows_superuser_at_limit(client):
    user = UserFactory(is_superuser=True)
    user.settings.place_creation_quota = 0
    user.settings.save()
    client.force_login(user)

    response = client.post(reverse(PLACE_CREATE_URL), data={})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
