import pytest

from django.urls import reverse
from django.contrib.auth import get_user_model

from events.tests.factories import EventFactory

User = get_user_model()


@pytest.mark.django_db
def test_successfully_login(django_app, user):
    user.set_password('acbCDE123$')
    user.save()

    response = django_app.get(reverse('users:login'), status=200)
    form = response.forms['login_form']
    form['username'] = user.username
    form['password'] = 'acbCDE123$'
    response = form.submit()
    assert response.status_code == 302


@pytest.mark.django_db
def test_successfully_register_user(django_app):
    response = django_app.get(reverse('users:register'), status=200)
    form = response.forms['register_form']
    form['username'] = 'pepito'
    form['first_name'] = 'Pepito'
    form['email'] = 'pepito@example.com'
    form['password1'] = 'acbCDE123$'
    form['password2'] = 'acbCDE123$'
    response = form.submit()
    assert response.status_code == 302

    user = User.objects.get(username='pepito')
    assert user.is_active is True


@pytest.mark.django_db
def test_register_user_email_already_exists(django_app, user):
    response = django_app.get(reverse('users:register'), status=200)
    form = response.forms['register_form']
    form['username'] = 'pepito'
    form['first_name'] = 'Pepito'
    form['email'] = user.email
    form['password1'] = 'acbCDE123$'
    form['password2'] = 'acbCDE123$'
    response = form.submit()
    assert response.status_code == 200


@pytest.mark.django_db
def test_successfully_shows_user_detail(django_app, user):
    response = django_app.get(
        reverse('users:user_detail', args=[user.username]),
        status=200
    )
    assert response.context['user_object'] == user
    assert user.first_name in response


@pytest.mark.django_db
def test_successfully_shows_user_detail_for_authenticated_user(django_app, user):
    response = django_app.get(
        reverse('users:user_detail', args=[user.username]),
        user=user,
        status=200
    )
    assert response.context['user_object'] == user
    assert user.first_name in response


@pytest.mark.django_db
def test_user_added_events_list_redirects_for_non_authenticated_user(django_app):
    response = django_app.get(
        reverse('users:user_added_events_list'),
        status=302
    )
    assert reverse('users:login') in response.location


@pytest.mark.django_db
def test_successfully_shows_user_events(django_app, user, other_user):
    first_event = EventFactory(created_by=user)
    second_event = EventFactory(created_by=user)

    other_user_event = EventFactory(
        created_by=other_user
    )

    response = django_app.get(
        reverse('users:user_added_events_list'),
        user=user,
        status=200
    )

    assert user == response.context['user_object']
    assert len(response.context['events']) == 2
    assert first_event in response.context['events']
    assert second_event in response.context['events']
    assert other_user_event not in response.context['events']
