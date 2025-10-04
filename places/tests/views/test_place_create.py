import pytest
from django.urls import reverse
from rest_framework import status

from places.models import Place
from places.tests.factories import PlaceFactory

VIEW_NAME = 'places:place_add'


def test_non_authenticated_user_cannot_create_place(django_app):
    """
    Ensure an unauthenticated user is redirected to the login page when requesting the place creation view.
    
    Asserts that accessing the place-add URL without authentication results in an HTTP 302 redirect whose Location header contains the login URL.
    """
    response = django_app.get(reverse(VIEW_NAME), status=status.HTTP_302_FOUND)
    assert reverse('users:login') in response.location


@pytest.mark.django_db
def test_successfully_create_place(django_app, user, city):
    """
    Verifies that an authenticated user can create a Place via the HTML form and is redirected after submission.
    
    Asserts that a new Place is created with created_by set to the submitting user, name 'Librería LERNER', address 'Cra 11 93', the provided city, and a non-null location, and that the response redirects to a URL containing the Place's absolute URL.
    """
    places_count = Place.objects.count()

    response = django_app.get(reverse(VIEW_NAME), user=user, status=status.HTTP_200_OK)

    form = response.forms['place_form']
    form['name'] = 'Librería LERNER'
    form['address'] = 'Cra 11 93'
    form['city'].force_value(city.id)
    form['location'] = 'POINT (36.04387479687501 -84.49382484631549)'

    response = form.submit()
    assert response.status_code == status.HTTP_302_FOUND

    assert Place.objects.count() == places_count + 1

    place = Place.objects.first()
    assert place.created_by == user
    assert place.name == 'Librería LERNER'
    assert place.address == 'Cra 11 93'
    assert place.city == city
    assert place.location is not None

    assert place.get_absolute_url() in response.location


@pytest.mark.django_db
def test_place_creation_quota(django_app, user, city):
    user_settings = user.settings

    user_settings.place_creation_quota = 2
    user_settings.save()

    assert user_settings.places_created_in_quota_period() == 0
    assert user_settings.reached_place_creation_quota() is False

    PlaceFactory(created_by=user)

    assert user_settings.places_created_in_quota_period() == 1
    assert user_settings.reached_place_creation_quota() is False

    response = django_app.get(reverse(VIEW_NAME), user=user, status=status.HTTP_200_OK)

    form = response.forms['place_form']
    form['name'] = 'Librería 1'
    form['address'] = 'Cra 11 93'
    form['city'].force_value(city.id)
    form['location'] = 'POINT (36.04387479687501 -84.49382484631549)'

    response = form.submit()
    assert response.status_code == status.HTTP_302_FOUND

    assert user_settings.places_created_in_quota_period() == 2
    assert user_settings.reached_place_creation_quota() is True

    place = Place.objects.order_by('-id')[0]
    assert place.created_by == user
    assert place.get_absolute_url() in response.location

    response = django_app.get(
        reverse(VIEW_NAME),
        user=user,
        status=status.HTTP_302_FOUND,
    )
    assert reverse("users:user_detail") in response.location

    assert user_settings.places_created_in_quota_period() == 2
    assert user_settings.reached_place_creation_quota() is True