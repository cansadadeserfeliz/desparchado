import pytest
from django.urls import reverse

from events.tests.factories import SpeakerFactory

VIEW_NAME = 'events:speaker_list'


@pytest.mark.django_db
def test_successfully_shows_speakers_list(django_app):
    first_speaker = SpeakerFactory()
    second_speaker = SpeakerFactory()
    response = django_app.get(reverse(VIEW_NAME), status=200)
    assert len(response.context['speakers']) == 2
    assert first_speaker in response.context['speakers']
    assert second_speaker in response.context['speakers']


@pytest.mark.django_db
def test_successfully_finds_speaker_by_name(django_app):
    first_speaker = SpeakerFactory(name='Pepito Perez')
    second_speaker = SpeakerFactory(name='Django Pony')
    search_term = 'Pony'
    response = django_app.get(
        reverse(VIEW_NAME), {'q': search_term}, status=200,
    )
    assert len(response.context['speakers']) == 1
    assert first_speaker not in response.context['speakers']
    assert second_speaker in response.context['speakers']
    assert response.context['search_string'] == search_term
    assert search_term in response.text


@pytest.mark.django_db
def test_successfully_finds_speaker_by_name_via_search_form(django_app):
    first_speaker = SpeakerFactory(name='Pepito Perez')
    second_speaker = SpeakerFactory(name='Django Pony')
    search_term = 'Pony'
    response = django_app.get(reverse(VIEW_NAME), status=200)

    form = response.forms['speaker_search_form']
    form['q'] = search_term
    response = form.submit()

    assert len(response.context['speakers']) == 1
    assert first_speaker not in response.context['speakers']
    assert second_speaker in response.context['speakers']
    assert response.context['search_string'] == search_term
    assert search_term in response.text
