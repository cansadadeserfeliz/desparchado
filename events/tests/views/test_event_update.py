import pytest
from django.urls import reverse

VIEW_NAME = 'events:event_update'


@pytest.mark.django_db
def test_does_not_allow_update_events_not_authenticated_users(django_app, event):
    response = django_app.get(
        reverse(VIEW_NAME, args=[event.id]), status=302,
    )
    assert reverse('account_login') in response.location


@pytest.mark.django_db
def test_does_not_allow_update_other_users_event(django_app, other_user, event):
    django_app.get(
        reverse(VIEW_NAME, args=[event.id]), user=other_user, status=403,
    )

@pytest.mark.django_db
def test_successfully_update_event(django_app, event_with_organizer):
    event = event_with_organizer
    user = event.created_by
    response = django_app.get(
        reverse(VIEW_NAME, args=[event.id]), user=user, status=200,
    )
    assert event.title in response

    form = response.forms['event_form']
    form['title'] = 'Presentación del libro de Julian Barnes'
    response = form.submit()
    assert response.status_code == 302
    response = response.follow()
    assert response.status_code == 200

    event.refresh_from_db()

    # Title was changed
    assert event.title == 'Presentación del libro de Julian Barnes'
