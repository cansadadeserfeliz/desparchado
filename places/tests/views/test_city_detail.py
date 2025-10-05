import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_show_details_of_city(django_app, event):
    city = event.place.city
    response = django_app.get(
        reverse('places:city_detail', args=[city.slug]), status=200,
    )
    assert city.name in response
    assert event.title in response
