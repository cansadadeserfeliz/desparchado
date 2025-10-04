import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_show_details_of_place(django_app, place):
    """
    Verify the place detail view renders the correct place and includes its name in the response.
    
    Performs a GET request to the place detail URL for the given place and asserts the response has status 200, that the response context contains the same Place instance, and that the place's name appears in the response content.
    
    Parameters:
        django_app: Test client fixture that can make HTTP requests to the Django app.
        place: Fixture providing a Place instance with a `slug` and `name`.
    """
    response = django_app.get(
        reverse('places:place_detail', args=[place.slug]), status=200,
    )
    assert response.context['place'] == place
    assert place.name in response
