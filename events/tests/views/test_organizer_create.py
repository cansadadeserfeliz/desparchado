import pytest
from django.urls import reverse

from events.models import Organizer

VIEW_NAME = 'events:organizer_add'


def test_non_authenticated_user_cannot_create_organizer(django_app):
    response = django_app.get(reverse(VIEW_NAME), status=302)
    assert reverse('account_login') in response.location


@pytest.mark.django_db
def test_successfully_create_organizer(django_app, user, image):
    organizers_count = Organizer.objects.count()

    response = django_app.get(
        reverse(VIEW_NAME),
        user=user,
        status=200,
    )

    form = response.forms['organizer_form']
    form['name'] = 'Librería LERNER'
    form['image'] = image
    form['description'] = 'Librería LERNER'
    form['website_url'] = 'https://www.librerialerner.com.co/'

    response = form.submit()

    assert Organizer.objects.count() == organizers_count + 1
    organizer = Organizer.objects.order_by('-id').first()

    assert response.status_code == 302
    assert organizer.get_absolute_url() in response.location
    response = response.follow()
    assert response.status_code == 200

    assert organizer.name == 'Librería LERNER'
    assert organizer.created_by == user
