import pytest

from places.services import search_places
from places.tests.factories import PlaceFactory


@pytest.mark.django_db
def test_search_places_returns_accent_insensitive_match():
    PlaceFactory(name='Jardín Botánico de Bogotá')
    results = list(search_places('jardin botanico'))
    assert len(results) == 1
    assert results[0].name == 'Jardín Botánico de Bogotá'


@pytest.mark.django_db
def test_search_places_returns_substring_match():
    PlaceFactory(name='Teatro Mayor Julio Mario Santo Domingo')
    results = list(search_places('teatro mayor'))
    assert len(results) == 1


@pytest.mark.django_db
def test_search_places_returns_first_items_when_q_is_empty():
    PlaceFactory(name='Teatro Mayor')
    results = list(search_places(''))
    assert len(results) == 1


@pytest.mark.django_db
def test_search_places_empty_when_q_is_single_char():
    PlaceFactory(name='Teatro Mayor')
    assert list(search_places('t')) == []


@pytest.mark.django_db
def test_search_places_excludes_non_matching():
    PlaceFactory(name='Jardín Botánico de Bogotá')
    PlaceFactory(name='Museo del Oro')
    results = list(search_places('jardin'))
    assert len(results) == 1
    assert results[0].name == 'Jardín Botánico de Bogotá'


@pytest.mark.django_db
def test_search_places_respects_limit():
    for i in range(5):
        PlaceFactory(name=f'Venue Test {i}')
    results = list(search_places('venue', limit=2))
    assert len(results) == 2


@pytest.mark.django_db
def test_search_places_ordered_by_name():
    PlaceFactory(name='Zócalo Cultural')
    PlaceFactory(name='Auditorio Principal')
    results = list(search_places('al'))
    names = [r.name for r in results]
    assert names == sorted(names)
