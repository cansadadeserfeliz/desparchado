import pytest

from django.urls import reverse

from ..models import Place
from .factories import PlaceFactory


@pytest.mark.django_db
def test_show_details_of_place(django_app, place):
    response = django_app.get(
        reverse('places:place_detail', args=[place.slug]),
        status=200
    )
    assert response.context['place'] == place
    assert place.name in response


@pytest.mark.django_db
def test_show_list_of_places(django_app, place):
    response = django_app.get(
        reverse('places:place_list'),
        status=200
    )
    assert place in response.context['places']
    assert place.name in response


@pytest.mark.django_db
def test_show_details_of_city(django_app, event):
    city = event.place.city
    response = django_app.get(
        reverse('places:city_detail', args=[city.slug]),
        status=200
    )
    assert city.name in response
    assert event.title in response


def test_non_authenticated_user_cannot_create_place(django_app):
    response = django_app.get(reverse('places:place_add'), status=302)
    assert reverse('users:login') in response.location


@pytest.mark.django_db
def test_successfully_create_place(django_app, user, city):
    places_count = Place.objects.count()

    response = django_app.get(
        reverse('places:place_add'),
        user=user,
        status=200,
    )

    form = response.forms['place_form']
    form['name'] = 'Librería LERNER'
    form['description'] = 'Librería LERNER'
    form['city'].force_value(city.id)
    form['location'] = 'POINT (36.04387479687501 -84.49382484631549)'

    response = form.submit()
    assert response.status_code == 302

    assert Place.objects.count() == places_count + 1

    place = Place.objects.first()
    assert place.created_by == user
    assert place.get_absolute_url() in response.location


@pytest.mark.django_db
def test_non_authenticated_user_cannot_update_place(django_app, place):
    response = django_app.get(reverse('places:place_update', args=[place.id]), status=302)
    assert reverse('users:login') in response.location


@pytest.mark.django_db
def test_successfully_update_place(django_app, user, place):
    place.created_by = user
    place.save()

    response = django_app.get(
        reverse('places:place_update', args=[place.id]),
        user=user,
        status=200,
    )

    form = response.forms['place_form']
    form['name'] = 'Librería LERNER'

    response = form.submit()
    assert response.status_code == 302

    place.refresh_from_db()

    # Name was changed
    assert place.name == 'Librería LERNER'

    assert place.get_absolute_url() in response.location


@pytest.mark.django_db
def test_successfully_get_place_wia_autocomplete(django_app, user):
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
def test_non_authenticated_user_cannot_get_place_wia_autocomplete(django_app):
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
