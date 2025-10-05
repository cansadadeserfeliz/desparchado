import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_show_list_of_places(django_app, place):
    response = django_app.get(reverse('places:place_list'), status=200)
    assert place in response.context['places']
    assert place.name in response
