import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_non_authenticated_user_cannot_update_place(django_app, place):
    """
    Ensure that unauthenticated requests to the place update page are redirected
    to the login page.
    """
    response = django_app.get(
        reverse('places:place_update', args=[place.id]), status=302,
    )
    assert reverse('account_login') in response.location


@pytest.mark.django_db
def test_successfully_update_place(django_app, user, place):
    """
    Verifies that an authenticated user can update a place's name via the update form
    and is redirected to the place's page.
    """
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
