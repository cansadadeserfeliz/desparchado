# Tests for target_audience mapping in dashboard.services.filbo.sync_filbo_event

import pytest

from dashboard.services.filbo import sync_filbo_event
from events.models import Event
from events.tests.factories import OrganizerFactory
from places.tests.factories import CityFactory
from specials.tests.factories import SpecialFactory
from users.tests.factories import UserFactory


def _make_row(target_audience: str = '', filbo_id: str = '99001') -> list[str]:
    """Return a minimal valid spreadsheet row for sync_filbo_event.

    Column positions (0-indexed): A=0 title, B=1 date, C=2 time, E=4 place,
    F=5 target_audience, G=6 category, H=7 link, J=9 description,
    K=10 organizer, L=11 participants.
    """
    link = f'https://www.filbo.com.co/descripcion-actividad/{filbo_id}/'
    return [
        'Test Event',           # A: title
        '2026-04-28',          # B: date
        '10:00',               # C: start_time
        '',                    # D: unused
        'Salón Ágora',         # E: place
        target_audience,       # F: target_audience
        'FILBo Literatura',    # G: category
        link,                  # H: link
        '',                    # I: unused
        'Test description',    # J: description
        '',                    # K: organizer
        '',                    # L: participants
    ]


@pytest.fixture()
def sync_deps():
    """Common dependencies for sync_filbo_event calls."""
    CityFactory(name='Bogotá')
    return {
        'special': SpecialFactory(),
        'default_organizer': OrganizerFactory(),
        'request_user': UserFactory(),
        'speakers_map': [],
        'organizers_map': [],
    }


@pytest.mark.django_db
def test_recognized_value_maps_to_early_childhood(sync_deps):
    sync_filbo_event(event_data=_make_row('age_under_6'), **sync_deps)
    event = Event.objects.get(source_id='FILBO2026_99001')
    assert event.target_audience == Event.TargetAudience.EARLY_CHILDHOOD


@pytest.mark.django_db
def test_age_13_27_maps_to_young_adult(sync_deps):
    sync_filbo_event(event_data=_make_row('age_13_27'), **sync_deps)
    event = Event.objects.get(source_id='FILBO2026_99001')
    assert event.target_audience == Event.TargetAudience.YOUNG_ADULT


@pytest.mark.django_db
def test_young_adult_maps_to_young_adult(sync_deps):
    sync_filbo_event(event_data=_make_row('young_adult'), **sync_deps)
    event = Event.objects.get(source_id='FILBO2026_99001')
    assert event.target_audience == Event.TargetAudience.YOUNG_ADULT


@pytest.mark.django_db
def test_book_professionals_maps_to_professionals(sync_deps):
    sync_filbo_event(event_data=_make_row('book_professionals'), **sync_deps)
    event = Event.objects.get(source_id='FILBO2026_99001')
    assert event.target_audience == Event.TargetAudience.PROFESSIONALS


@pytest.mark.django_db
def test_empty_target_audience_stores_blank(sync_deps):
    sync_filbo_event(event_data=_make_row(''), **sync_deps)
    event = Event.objects.get(source_id='FILBO2026_99001')
    assert event.target_audience == ''


@pytest.mark.django_db
def test_unrecognized_value_stores_blank_and_warns(sync_deps, caplog):
    import logging
    with caplog.at_level(logging.WARNING, logger='dashboard.services.filbo'):
        sync_filbo_event(event_data=_make_row('unrecognized_value'), **sync_deps)
    event = Event.objects.get(source_id='FILBO2026_99001')
    assert event.target_audience == ''
    assert 'unrecognized_value' in caplog.text


@pytest.mark.django_db
def test_resync_updates_target_audience(sync_deps):
    sync_filbo_event(event_data=_make_row('age_under_6', filbo_id='99002'), **sync_deps)
    sync_filbo_event(event_data=_make_row('age_over_27', filbo_id='99002'), **sync_deps)
    event = Event.objects.get(source_id='FILBO2026_99002')
    assert event.target_audience == Event.TargetAudience.ADULTS
