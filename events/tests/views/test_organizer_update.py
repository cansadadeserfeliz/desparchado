import pytest
from django.urls import reverse

VIEW_NAME = 'events:organizer_update'


@pytest.mark.django_db
def test_non_authenticated_user_cannot_update_organizer(django_app, organizer):
    response = django_app.get(
        reverse(VIEW_NAME, args=[organizer.slug]), status=302,
    )
    assert reverse('account_login') in response.location


@pytest.mark.django_db
def test_successfully_update_organizer(django_app, user, organizer):
    organizer.created_by = user
    organizer.save()

    response = django_app.get(
        reverse(VIEW_NAME, args=[organizer.slug]),
        user=user,
        status=200,
    )

    form = response.forms['organizer_form']
    form['name'] = 'Librería Nacional'

    response = form.submit()
    assert response.status_code == 302

    organizer.refresh_from_db()

    assert organizer.created_by == user
    assert organizer.name == 'Librería Nacional'
    assert organizer.get_absolute_url() in response.location
