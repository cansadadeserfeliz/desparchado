# Tests for dashboard.services.filbo.get_organizers

import pytest

from dashboard.services.filbo import get_organizers
from events.models import Organizer
from events.tests.factories import OrganizerFactory
from users.tests.factories import UserFactory


def _organizers_map(*pairs: tuple[str, str]) -> list[dict[str, str]]:
    """Build an organizers_map list from (FILBO_NAME, CANONICAL_NAME) pairs."""
    return [
        {'FILBO_NAME': filbo, 'CANONICAL_NAME': canonical}
        for filbo, canonical in pairs
    ]


# ---------------------------------------------------------------------------
# Default organizer is always first
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_organizers_always_returns_default_organizer_first():
    user = UserFactory()
    default = OrganizerFactory()
    result = get_organizers('', [], default, user)
    assert result[0] == default


@pytest.mark.django_db
def test_get_organizers_blank_name_returns_only_default():
    user = UserFactory()
    default = OrganizerFactory()
    result = get_organizers('', [], default, user)
    assert result == [default]


@pytest.mark.django_db
def test_get_organizers_whitespace_only_name_returns_only_default():
    user = UserFactory()
    default = OrganizerFactory()
    result = get_organizers('   ', [], default, user)
    assert result == [default]


# ---------------------------------------------------------------------------
# FILBO_NAME match — organizer does not yet exist → created and appended
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_organizers_creates_organizer_when_canonical_name_not_in_db():
    user = UserFactory()
    default = OrganizerFactory()
    organizers_map = _organizers_map(('FILBo Author', 'Canonical Author'))

    result = get_organizers('FILBo Author', organizers_map, default, user)

    assert len(result) == 2
    assert result[0] == default
    assert result[1].name == 'Canonical Author'
    assert Organizer.objects.filter(name='Canonical Author').exists()


@pytest.mark.django_db
def test_get_organizers_new_organizer_has_correct_created_by():
    user = UserFactory()
    default = OrganizerFactory()
    organizers_map = _organizers_map(('FILBo Author', 'Canonical Author'))

    result = get_organizers('FILBo Author', organizers_map, default, user)

    assert result[1].created_by == user


# ---------------------------------------------------------------------------
# FILBO_NAME match — organizer already exists → fetched and appended
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_organizers_fetches_existing_organizer_by_canonical_name():
    user = UserFactory()
    default = OrganizerFactory()
    existing = OrganizerFactory(name='Canonical Author')
    organizers_map = _organizers_map(('FILBo Author', 'Canonical Author'))

    result = get_organizers('FILBo Author', organizers_map, default, user)

    assert len(result) == 2
    assert result[1] == existing
    assert Organizer.objects.filter(name='Canonical Author').count() == 1


# ---------------------------------------------------------------------------
# FILBO_NAME match is case-insensitive and strips whitespace
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_organizers_filbo_name_match_is_case_insensitive():
    user = UserFactory()
    default = OrganizerFactory()
    organizers_map = _organizers_map(('FILBO AUTHOR', 'Canonical Author'))

    result = get_organizers('filbo author', organizers_map, default, user)

    assert len(result) == 2
    assert result[1].name == 'Canonical Author'


@pytest.mark.django_db
def test_get_organizers_organizer_name_with_leading_trailing_spaces_matches():
    user = UserFactory()
    default = OrganizerFactory()
    organizers_map = _organizers_map(('  FILBo Author  ', 'Canonical Author'))

    result = get_organizers('  FILBo Author  ', organizers_map, default, user)

    assert len(result) == 2
    assert result[1].name == 'Canonical Author'


@pytest.mark.django_db
def test_get_organizers_canonical_name_is_stripped_before_get_or_create():
    user = UserFactory()
    default = OrganizerFactory()
    organizers_map = _organizers_map(('FILBo Author', '  Canonical Author  '))

    result = get_organizers('FILBo Author', organizers_map, default, user)

    assert result[1].name == 'Canonical Author'


# ---------------------------------------------------------------------------
# Blank CANONICAL_NAME in map → no second organizer
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_organizers_blank_canonical_name_produces_no_second_organizer():
    user = UserFactory()
    default = OrganizerFactory()
    organizers_map = _organizers_map(('FILBo Author', ''))

    result = get_organizers('FILBo Author', organizers_map, default, user)

    assert result == [default]


@pytest.mark.django_db
def test_get_organizers_whitespace_canonical_name_produces_no_second_organizer():
    user = UserFactory()
    default = OrganizerFactory()
    organizers_map = _organizers_map(('FILBo Author', '   '))

    result = get_organizers('FILBo Author', organizers_map, default, user)

    assert result == [default]


# ---------------------------------------------------------------------------
# No FILBO_NAME match → fallback to iexact lookup on organizer_name
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_organizers_fallback_appends_organizer_found_by_iexact():
    user = UserFactory()
    default = OrganizerFactory()
    existing = OrganizerFactory(name='Unknown Org')
    organizers_map = _organizers_map(('Some Other Name', 'Canonical Other'))

    result = get_organizers('Unknown Org', organizers_map, default, user)

    assert len(result) == 2
    assert result[1] == existing


@pytest.mark.django_db
def test_get_organizers_fallback_iexact_is_case_insensitive():
    user = UserFactory()
    default = OrganizerFactory()
    existing = OrganizerFactory(name='Unknown Org')
    organizers_map = _organizers_map(('Some Other Name', 'Canonical Other'))

    result = get_organizers('unknown org', organizers_map, default, user)

    assert len(result) == 2
    assert result[1] == existing


@pytest.mark.django_db
def test_get_organizers_fallback_returns_only_default_when_not_found():
    user = UserFactory()
    default = OrganizerFactory()

    result = get_organizers(
        'Nonexistent Org', [], default, user,
    )

    assert result == [default]


# ---------------------------------------------------------------------------
# Empty organizers_map always triggers fallback path
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_organizers_empty_map_uses_fallback_when_organizer_exists():
    user = UserFactory()
    default = OrganizerFactory()
    existing = OrganizerFactory(name='Solo Org')

    result = get_organizers('Solo Org', [], default, user)

    assert result == [default, existing]


@pytest.mark.django_db
def test_get_organizers_empty_map_returns_only_default_when_no_match():
    user = UserFactory()
    default = OrganizerFactory()

    result = get_organizers('Solo Org', [], default, user)

    assert result == [default]
