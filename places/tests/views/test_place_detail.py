import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_show_details_of_place(django_app, place):
    response = django_app.get(
        reverse('places:place_detail', args=[place.slug]), status=200,
    )
    assert response.context['place'] == place
    assert place.name in response
