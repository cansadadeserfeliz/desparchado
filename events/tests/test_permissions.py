import pytest
from rest_framework.test import APIRequestFactory

from events.permissions import (
    EventCreationQuotaPermission,
    OrganizerCreationQuotaPermission,
    SpeakerCreationQuotaPermission,
)
from places.permissions import PlaceCreationQuotaPermission
from users.tests.factories import UserFactory

factory = APIRequestFactory()


def _post_request(user):
    request = factory.post('/')
    request.user = user
    return request


def _get_request(user):
    request = factory.get('/')
    request.user = user
    return request


# ---------------------------------------------------------------------------
# EventCreationQuotaPermission
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_event_quota_permission_blocks_user_at_limit():
    user = UserFactory()
    user.settings.event_creation_quota = 0
    user.settings.save()
    assert EventCreationQuotaPermission().has_permission(_post_request(user), None) is False


@pytest.mark.django_db
def test_event_quota_permission_allows_user_under_limit():
    user = UserFactory()
    assert EventCreationQuotaPermission().has_permission(_post_request(user), None) is True


@pytest.mark.django_db
def test_event_quota_permission_allows_superuser_at_limit():
    user = UserFactory(is_superuser=True)
    user.settings.event_creation_quota = 0
    user.settings.save()
    assert EventCreationQuotaPermission().has_permission(_post_request(user), None) is True


@pytest.mark.django_db
def test_event_quota_permission_allows_safe_methods():
    user = UserFactory()
    user.settings.event_creation_quota = 0
    user.settings.save()
    assert EventCreationQuotaPermission().has_permission(_get_request(user), None) is True


# ---------------------------------------------------------------------------
# OrganizerCreationQuotaPermission
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_organizer_quota_permission_allows_safe_methods():
    user = UserFactory()
    user.settings.organizer_creation_quota = 0
    user.settings.save()
    assert OrganizerCreationQuotaPermission().has_permission(_get_request(user), None) is True


@pytest.mark.django_db
def test_organizer_quota_permission_blocks_user_at_limit():
    user = UserFactory()
    user.settings.organizer_creation_quota = 0
    user.settings.save()
    assert OrganizerCreationQuotaPermission().has_permission(_post_request(user), None) is False


@pytest.mark.django_db
def test_organizer_quota_permission_allows_user_under_limit():
    user = UserFactory()
    assert OrganizerCreationQuotaPermission().has_permission(_post_request(user), None) is True


@pytest.mark.django_db
def test_organizer_quota_permission_allows_superuser_at_limit():
    user = UserFactory(is_superuser=True)
    user.settings.organizer_creation_quota = 0
    user.settings.save()
    assert OrganizerCreationQuotaPermission().has_permission(_post_request(user), None) is True


# ---------------------------------------------------------------------------
# SpeakerCreationQuotaPermission
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_speaker_quota_permission_allows_safe_methods():
    user = UserFactory()
    user.settings.speaker_creation_quota = 0
    user.settings.save()
    assert SpeakerCreationQuotaPermission().has_permission(_get_request(user), None) is True


@pytest.mark.django_db
def test_speaker_quota_permission_blocks_user_at_limit():
    user = UserFactory()
    user.settings.speaker_creation_quota = 0
    user.settings.save()
    assert SpeakerCreationQuotaPermission().has_permission(_post_request(user), None) is False


@pytest.mark.django_db
def test_speaker_quota_permission_allows_user_under_limit():
    user = UserFactory()
    assert SpeakerCreationQuotaPermission().has_permission(_post_request(user), None) is True


@pytest.mark.django_db
def test_speaker_quota_permission_allows_superuser_at_limit():
    user = UserFactory(is_superuser=True)
    user.settings.speaker_creation_quota = 0
    user.settings.save()
    assert SpeakerCreationQuotaPermission().has_permission(_post_request(user), None) is True


# ---------------------------------------------------------------------------
# PlaceCreationQuotaPermission
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_place_quota_permission_allows_safe_methods():
    user = UserFactory()
    user.settings.place_creation_quota = 0
    user.settings.save()
    assert PlaceCreationQuotaPermission().has_permission(_get_request(user), None) is True


@pytest.mark.django_db
def test_place_quota_permission_blocks_user_at_limit():
    user = UserFactory()
    user.settings.place_creation_quota = 0
    user.settings.save()
    assert PlaceCreationQuotaPermission().has_permission(_post_request(user), None) is False


@pytest.mark.django_db
def test_place_quota_permission_allows_user_under_limit():
    user = UserFactory()
    assert PlaceCreationQuotaPermission().has_permission(_post_request(user), None) is True


@pytest.mark.django_db
def test_place_quota_permission_allows_superuser_at_limit():
    user = UserFactory(is_superuser=True)
    user.settings.place_creation_quota = 0
    user.settings.save()
    assert PlaceCreationQuotaPermission().has_permission(_post_request(user), None) is True
