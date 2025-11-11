import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from events.tests.factories import EventFactory

User = get_user_model()


@pytest.mark.django_db
def test_successfully_login_with_email(django_app, user):
    user.set_password('acbCDE123$')
    user.save()

    response = django_app.get(reverse('account_login'), status=status.HTTP_200_OK)
    form = response.forms[0]
    form['login'] = user.email
    form['password'] = 'acbCDE123$'
    response = form.submit()
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_successfully_register_user(django_app):
    response = django_app.get(reverse('account_signup'), status=status.HTTP_200_OK)
    form = response.forms[0]
    form['email'] = 'pepito@example.com'
    form['password1'] = 'acbCDE123$'
    form['password2'] = 'acbCDE123$'
    response = form.submit()
    assert response.status_code == status.HTTP_302_FOUND

    user = User.objects.get(email='pepito@example.com')
    assert user.is_active is True
    assert user.username == 'pepito'
    assert user.settings is not None, 'UserSettings were created'


@pytest.mark.django_db
def test_register_user_email_already_exists(django_app, user):
    response = django_app.get(reverse('account_signup'), status=status.HTTP_200_OK)
    form = response.forms[0]
    form['email'] = user.email
    form['password1'] = 'acbCDE123$'
    form['password2'] = 'acbCDE123$'
    response = form.submit()
    assert response.status_code == status.HTTP_302_FOUND
    assert reverse("account_email_verification_sent") in response.location


@pytest.mark.django_db
def test_successfully_reset_password(django_app, user):
    response = django_app.get(
        reverse('account_reset_password'),
        status=status.HTTP_200_OK,
    )
    form = response.forms[0]
    form['email'] = user.email
    response = form.submit()
    assert response.status_code == status.HTTP_302_FOUND
    assert reverse("account_reset_password_done") in response.location


@pytest.mark.django_db
def test_successfully_shows_user_detail_for_authenticated_user(django_app, user):
    django_app.get(
        reverse('users:user_detail'), user=user, status=status.HTTP_200_OK,
    )


def test_profile_redirects_for_anonymous_user(django_app):
    response = django_app.get(
        reverse('users:user_detail'),
        status=status.HTTP_302_FOUND,
    )
    assert reverse('account_login') in response.location


@pytest.mark.django_db
def test_user_added_events_list_redirects_for_non_authenticated_user(django_app):
    response = django_app.get(
        reverse('users:user_added_events_list'),
        status=status.HTTP_302_FOUND,
    )
    assert reverse('account_login') in response.location


@pytest.mark.django_db
def test_successfully_shows_user_events(django_app, user, other_user):
    first_event = EventFactory(created_by=user)
    second_event = EventFactory(created_by=user)

    other_user_event = EventFactory(created_by=other_user)

    response = django_app.get(
        reverse('users:user_added_events_list'), user=user, status=status.HTTP_200_OK,
    )

    assert user == response.context['user_object']
    assert len(response.context['events']) == 2
    assert first_event in response.context['events']
    assert second_event in response.context['events']
    assert other_user_event not in response.context['events']
