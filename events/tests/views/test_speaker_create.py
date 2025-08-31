import pytest
from django.urls import reverse

from events.models import Speaker

VIEW_NAME = 'events:speaker_add'


def test_non_authenticated_user_cannot_create_speaker(django_app):
    response = django_app.get(reverse(VIEW_NAME), status=302)
    assert reverse('users:login') in response.location


@pytest.mark.django_db
def test_successfully_create_speaker(django_app, user):
    speakers_count = Speaker.objects.count()

    response = django_app.get(reverse(VIEW_NAME), user=user, status=200)

    form = response.forms['speaker_form']
    form['name'] = 'Julian Barnes'
    form['description'] = 'English writer'

    response = form.submit()

    assert Speaker.objects.count() == speakers_count + 1
    speaker = Speaker.objects.order_by('-id').first()

    assert response.status_code == 302
    assert speaker.get_absolute_url() in response.location

    response = response.follow()
    assert response.status_code == 200

    assert speaker.name in response.text
    assert speaker.created_by == user
