import pytest
from django.urls import reverse

from places.tests.factories import PlaceFactory


@pytest.mark.django_db
def test_successfully_get_place_via_autocomplete(django_app, user):
    place = PlaceFactory(name='Librería Nacional')
    # Create a place that won't appear in search results
    PlaceFactory(name='Museo de Arte Moderno')

    search_term = 'Nacional'
    response = django_app.get(
        reverse('places:place_autocomplete'),
        {'q': search_term},
        user=user,
        status=200,
    )
    response_json = response.json

    assert 'results' in response_json
    results = response_json['results']
    assert len(results) == 1
    assert results[0]['id'] == str(place.id)
    assert results[0]['selected_text'] == place.name


@pytest.mark.django_db
def test_non_authenticated_user_cannot_get_place_via_autocomplete(django_app):
    PlaceFactory(name='Librería Nacional')
    search_term = 'Nacional'
    response = django_app.get(
        reverse('places:place_autocomplete'),
        {'q': search_term},
        status=200,
    )
    response_json = response.json

    assert 'results' in response_json
    assert len(response_json['results']) == 0
