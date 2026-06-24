import io

import pytest
from django.contrib.gis.geos import Point
from django.urls import reverse
from PIL import Image
from rest_framework import status

from places.models import Place
from places.tests.factories import CityFactory, PlaceFactory
from users.tests.factories import UserFactory

CREATE_URL = 'places_api:place_create'


def _make_image_file(filename: str = 'test.jpg') -> io.BytesIO:
    img = Image.new('RGB', (10, 10), color='red')
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.name = filename
    buf.seek(0)
    return buf


def _valid_payload(city_id: int) -> dict:
    return {
        'name': 'Lugar de Prueba',
        'address': 'Calle 10 # 5-20',
        'city': city_id,
        'lat': 4.7110,
        'lng': -74.0721,
        'website_url': 'https://example.com',
        'image_source_url': 'https://example.com/image.jpg',
    }


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_unauthenticated_post_is_rejected(client):
    """SessionAuthentication returns 403 for anonymous users."""
    city = CityFactory()
    response = client.post(reverse(CREATE_URL), data=_valid_payload(city.pk))
    assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# Successful creation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_valid_post_creates_place_and_returns_201(client):
    user = UserFactory()
    city = CityFactory()
    client.force_login(user)

    response = client.post(reverse(CREATE_URL), data=_valid_payload(city.pk))

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert 'id' in data
    assert data['name'] == 'Lugar de Prueba'


@pytest.mark.django_db
def test_valid_post_sets_created_by(client):
    user = UserFactory()
    city = CityFactory()
    client.force_login(user)

    response = client.post(reverse(CREATE_URL), data=_valid_payload(city.pk))

    assert response.status_code == status.HTTP_201_CREATED
    place = Place.objects.get(name='Lugar de Prueba')
    assert place.created_by == user


@pytest.mark.django_db
def test_valid_post_response_id_matches_created_place(client):
    user = UserFactory()
    city = CityFactory()
    client.force_login(user)

    response = client.post(reverse(CREATE_URL), data=_valid_payload(city.pk))

    place = Place.objects.get(name='Lugar de Prueba')
    assert response.json()['id'] == place.pk


@pytest.mark.django_db
def test_valid_post_sets_location_point_with_correct_coordinates(client):
    user = UserFactory()
    city = CityFactory()
    client.force_login(user)

    lat = 4.7110
    lng = -74.0721
    payload = _valid_payload(city.pk)
    payload['lat'] = lat
    payload['lng'] = lng

    client.post(reverse(CREATE_URL), data=payload)

    place = Place.objects.get(name='Lugar de Prueba')
    assert isinstance(place.location, Point)
    assert abs(place.location.x - lng) < 1e-6  # x = longitude
    assert abs(place.location.y - lat) < 1e-6  # y = latitude


@pytest.mark.django_db
def test_valid_post_with_image_stores_image(client):
    user = UserFactory()
    city = CityFactory()
    client.force_login(user)

    payload = _valid_payload(city.pk)
    payload['image'] = _make_image_file()

    response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_201_CREATED
    place = Place.objects.get(name='Lugar de Prueba')
    assert bool(place.image)


# ---------------------------------------------------------------------------
# Required-field validation → 400
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_missing_name_returns_400(client):
    user = UserFactory()
    city = CityFactory()
    client.force_login(user)

    payload = _valid_payload(city.pk)
    del payload['name']
    response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'name' in response.json()


@pytest.mark.django_db
def test_duplicate_name_returns_400(client):
    user = UserFactory()
    city = CityFactory()
    client.force_login(user)
    PlaceFactory(name='Lugar Duplicado')

    payload = _valid_payload(city.pk)
    payload['name'] = 'Lugar Duplicado'
    response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'name' in response.json()


@pytest.mark.django_db
def test_name_too_short_returns_400(client):
    user = UserFactory()
    city = CityFactory()
    client.force_login(user)

    payload = _valid_payload(city.pk)
    payload['name'] = 'AB'
    response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'name' in response.json()


@pytest.mark.django_db
def test_address_too_short_returns_400(client):
    user = UserFactory()
    city = CityFactory()
    client.force_login(user)

    payload = _valid_payload(city.pk)
    payload['address'] = 'AB'
    response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'address' in response.json()


@pytest.mark.django_db
def test_missing_address_returns_400(client):
    user = UserFactory()
    city = CityFactory()
    client.force_login(user)

    payload = _valid_payload(city.pk)
    del payload['address']
    response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'address' in response.json()


@pytest.mark.django_db
def test_missing_city_returns_400(client):
    user = UserFactory()
    client.force_login(user)

    payload = {
        'name': 'Lugar Sin Ciudad',
        'address': 'Calle 10 # 5-20',
        'lat': 4.7110,
        'lng': -74.0721,
    }
    response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'city' in response.json()


@pytest.mark.django_db
def test_missing_lat_returns_400(client):
    user = UserFactory()
    city = CityFactory()
    client.force_login(user)

    payload = _valid_payload(city.pk)
    del payload['lat']
    response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'lat' in response.json()


@pytest.mark.django_db
def test_missing_lng_returns_400(client):
    user = UserFactory()
    city = CityFactory()
    client.force_login(user)

    payload = _valid_payload(city.pk)
    del payload['lng']
    response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'lng' in response.json()


# ---------------------------------------------------------------------------
# Colombia bounding box validation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_lat_outside_colombia_returns_400(client):
    user = UserFactory()
    city = CityFactory()
    client.force_login(user)

    payload = _valid_payload(city.pk)
    payload['lat'] = 20.0  # valid globally, north of Colombia
    response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'lat' in response.json()


@pytest.mark.django_db
def test_lng_outside_colombia_returns_400(client):
    user = UserFactory()
    city = CityFactory()
    client.force_login(user)

    payload = _valid_payload(city.pk)
    payload['lng'] = -60.0  # valid globally, east of Colombia
    response = client.post(reverse(CREATE_URL), data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'lng' in response.json()


# ---------------------------------------------------------------------------
# Quota enforcement
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_quota_exceeded_returns_403(client):
    user = UserFactory()
    user.settings.place_creation_quota = 0
    user.settings.save()
    city = CityFactory()
    client.force_login(user)

    response = client.post(reverse(CREATE_URL), data=_valid_payload(city.pk))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()['detail'] == 'Hoy alcanzaste el límite de nuevos lugares.'


@pytest.mark.django_db
def test_superuser_bypasses_quota(client):
    user = UserFactory(is_superuser=True)
    user.settings.place_creation_quota = 0
    user.settings.save()
    city = CityFactory()
    client.force_login(user)

    response = client.post(reverse(CREATE_URL), data=_valid_payload(city.pk))

    assert response.status_code == status.HTTP_201_CREATED
