import pytest

from events.services import search_organizers, search_speakers
from events.tests.factories import OrganizerFactory, SpeakerFactory


@pytest.mark.django_db
def test_search_organizers_returns_accent_insensitive_match():
    OrganizerFactory(name='Biblioteca Luis Ángel Arango')
    results = list(search_organizers('luis angel arango'))
    assert len(results) == 1
    assert results[0].name == 'Biblioteca Luis Ángel Arango'


@pytest.mark.django_db
def test_search_organizers_returns_substring_match():
    OrganizerFactory(name='Feria Internacional del Libro')
    results = list(search_organizers('feria internacional'))
    assert len(results) == 1


@pytest.mark.django_db
def test_search_organizers_returns_first_items_when_q_is_empty():
    OrganizerFactory(name='Feria Internacional del Libro')
    results = list(search_organizers(''))
    assert len(results) == 1


@pytest.mark.django_db
def test_search_organizers_empty_when_q_is_single_char():
    OrganizerFactory(name='Feria Internacional del Libro')
    assert list(search_organizers('f')) == []


@pytest.mark.django_db
def test_search_organizers_excludes_non_matching():
    OrganizerFactory(name='Biblioteca Luis Ángel Arango')
    OrganizerFactory(name='Museo Nacional')
    results = list(search_organizers('biblioteca'))
    assert len(results) == 1
    assert results[0].name == 'Biblioteca Luis Ángel Arango'


@pytest.mark.django_db
def test_search_organizers_respects_limit():
    for i in range(5):
        OrganizerFactory(name=f'Organizer Test {i}')
    results = list(search_organizers('organizer', limit=3))
    assert len(results) == 3


@pytest.mark.django_db
def test_search_organizers_ordered_by_name():
    OrganizerFactory(name='Zebra Corp')
    OrganizerFactory(name='Alpha Corp')
    results = list(search_organizers('corp'))
    assert results[0].name == 'Alpha Corp'
    assert results[1].name == 'Zebra Corp'


@pytest.mark.django_db
def test_search_speakers_returns_accent_insensitive_match():
    SpeakerFactory(name='José García')
    results = list(search_speakers('jose garcia'))
    assert len(results) == 1
    assert results[0].name == 'José García'


@pytest.mark.django_db
def test_search_speakers_returns_first_items_when_q_is_empty():
    SpeakerFactory(name='José García')
    results = list(search_speakers(''))
    assert len(results) == 1


@pytest.mark.django_db
def test_search_speakers_empty_when_q_is_single_char():
    SpeakerFactory(name='José García')
    assert list(search_speakers('j')) == []


@pytest.mark.django_db
def test_search_speakers_excludes_non_matching():
    SpeakerFactory(name='José García')
    SpeakerFactory(name='Ana Martínez')
    results = list(search_speakers('garcia'))
    assert len(results) == 1
    assert results[0].name == 'José García'


@pytest.mark.django_db
def test_search_speakers_respects_limit():
    for i in range(5):
        SpeakerFactory(name=f'Speaker Test {i}')
    results = list(search_speakers('speaker', limit=2))
    assert len(results) == 2


@pytest.mark.django_db
def test_search_speakers_ordered_by_name():
    SpeakerFactory(name='Zebra Ponente')
    SpeakerFactory(name='Alpha Ponente')
    results = list(search_speakers('ponente'))
    assert results[0].name == 'Alpha Ponente'
    assert results[1].name == 'Zebra Ponente'
