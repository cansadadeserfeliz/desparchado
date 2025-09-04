import pytest
from django.urls import reverse

VIEW_NAME = 'events:speaker_update'


@pytest.mark.django_db
def test_non_authenticated_user_cannot_update_speaker(django_app, speaker):
    response = django_app.get(
        reverse(VIEW_NAME, args=[speaker.slug]), status=302,
    )
    assert reverse('users:login') in response.location


@pytest.mark.django_db
def test_successfully_update_speaker(django_app, user, speaker):
    speaker.created_by = user
    speaker.save()

    response = django_app.get(
        reverse(VIEW_NAME, args=[speaker.slug]),
        user=user,
        status=200,
    )

    form = response.forms['speaker_form']
    form['name'] = 'Chimamanda Ngozi Adichie'

    response = form.submit()
    assert response.status_code == 302

    speaker.refresh_from_db()

    assert speaker.name == 'Chimamanda Ngozi Adichie'
    assert speaker.get_absolute_url() in response.location

    response = response.follow()
    assert response.status_code == 200
    assert speaker.name in response
