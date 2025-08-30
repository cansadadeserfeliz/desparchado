from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from ..models import Event, Organizer, Speaker
from .factories import SpeakerFactory


@pytest.mark.django_db
def test_events_appearance_in_event_list(
    django_app, event, not_published_event, not_approved_event, past_event,
):
    response = django_app.get(reverse('events:event_list'), status=200)

    assert event in response.context['events']
    assert not_published_event not in response.context['events']
    assert not_approved_event not in response.context['events']
    assert past_event not in response.context['events']


@pytest.mark.django_db
def test_filter_events_by_city_in_event_list(django_app, event, other_event):
    city_filter = event.place.city.slug
    response = django_app.get(
        reverse('events:event_list') + f'?city={city_filter}', status=200,
    )
    assert event in response.context['events']
    assert other_event not in response.context['events']


@pytest.mark.django_db
def test_search_events_by_title(django_app, event, other_event):
    event.title = (
        'Después de la siesta, despertó con el rostro abuhado y los sueños revueltos'
    )
    event.save()

    response = django_app.get(reverse('events:event_list') + '?q=despues', status=200)
    assert event in response.context['events']
    assert other_event not in response.context['events']


@pytest.mark.django_db
def test_search_events_speaker_name(django_app, event, speaker, other_event):
    speaker.name = 'Iñaki Rojas'
    speaker.save()
    event.speakers.add(speaker)

    response = django_app.get(reverse('events:event_list') + '?q=inaki', status=200)
    assert event in response.context['events']
    assert other_event not in response.context['events']


@pytest.mark.django_db
def test_show_details_of_event(django_app, event):
    response = django_app.get(
        reverse('events:event_detail', args=[event.slug]), status=200,
    )
    assert event == response.context['event']


@pytest.mark.django_db
def test_events_appearance_in_past_event_list(
    django_app, event, not_published_event, not_approved_event, past_event,
):
    response = django_app.get(reverse('events:past_event_list'), status=200)

    assert past_event in response.context['events']
    assert event not in response.context['events']
    assert not_published_event not in response.context['events']
    assert not_approved_event not in response.context['events']


@pytest.mark.django_db
def test_show_details_of_not_published_event(django_app, not_published_event):
    django_app.get(
        reverse('events:event_detail', args=[not_published_event.slug]), status=404,
    )


@pytest.mark.django_db
def test_show_details_of_not_approved_event(django_app, not_approved_event):
    django_app.get(
        reverse('events:event_detail', args=[not_approved_event.slug]), status=404,
    )


@pytest.mark.django_db
def test_not_authenticated_user_cannot_create_event(django_app):
    response = django_app.get(reverse('events:add_event'), status=302)
    assert reverse('users:login') in response.location


@pytest.mark.django_db
def test_successfully_create_event(django_app, user, organizer, place):
    events_count = Event.objects.count()
    response = django_app.get(
        reverse('events:add_event'),
        user=user,
        status=200,
    )

    form = response.forms['event_form']
    form['title'] = 'Presentación del libro de Julian Barnes'
    form['description'] = (
        'Hasta hace poco he visto a Julian Barnes '
        'como uno de esos escritores que nos interesan, '
        'cuya lectura creemos inminente, '
        'pero que vamos aplazando año tras año '
        'sin ningún motivo concreto.'
    )
    form['event_date'] = (timezone.now() + timedelta(days=1)).strftime('%d/%m/%Y %H:%M')
    form['event_end_date'] = (timezone.now() + timedelta(days=2)).strftime(
        '%d/%m/%Y %H:%M',
    )
    form['event_source_url'] = 'https://example.com'
    form['organizers'].force_value([organizer.id])
    form['place'].force_value(place.id)

    response = form.submit()
    assert response.status_code == 302

    assert Event.objects.count() == events_count + 1
    event = Event.objects.first()
    assert event.created_by == user

    assert event.get_absolute_url() in response.location


@pytest.mark.django_db
def test_does_not_allow_update_events_not_authenticated_users(django_app, event):
    response = django_app.get(
        reverse('events:event_update', args=[event.id]), status=302,
    )
    assert reverse('users:login') in response.location


@pytest.mark.django_db
def test_does_not_allow_update_other_users_event(django_app, other_user, event):
    django_app.get(
        reverse('events:event_update', args=[event.id]), user=other_user, status=403,
    )


@pytest.mark.django_db
def test_successfully_update_event(django_app, event_with_organizer):
    event = event_with_organizer
    user = event.created_by
    response = django_app.get(
        reverse('events:event_update', args=[event.id]), user=user, status=200,
    )
    assert event.title in response

    form = response.forms['event_form']
    form['title'] = 'Presentación del libro de Julian Barnes'
    form.submit().follow()

    event.refresh_from_db()

    # Title was changed
    assert event.title == 'Presentación del libro de Julian Barnes'


@pytest.mark.django_db
def test_show_details_of_organizer(django_app, organizer):
    response = django_app.get(
        reverse('events:organizer_detail', args=[organizer.slug]), status=200,
    )
    assert response.context['organizer'] == organizer
    assert organizer.name in response


@pytest.mark.django_db
def test_successfully_show_details_of_speaker(django_app, speaker):
    response = django_app.get(
        reverse('events:speaker_detail', args=[speaker.slug]), status=200,
    )
    assert response.context['speaker'] == speaker


@pytest.mark.django_db
def test_successfully_shows_speakers_list(django_app):
    first_speaker = SpeakerFactory()
    second_speaker = SpeakerFactory()
    response = django_app.get(reverse('events:speaker_list'), status=200)
    assert len(response.context['speakers']) == 2
    assert first_speaker in response.context['speakers']
    assert second_speaker in response.context['speakers']


@pytest.mark.django_db
def test_successfully_finds_speaker_by_name(django_app):
    first_speaker = SpeakerFactory(name='Pepito Perez')
    second_speaker = SpeakerFactory(name='Django Pony')
    search_term = 'Pony'
    response = django_app.get(
        reverse('events:speaker_list'), {'q': search_term}, status=200,
    )
    assert len(response.context['speakers']) == 1
    assert first_speaker not in response.context['speakers']
    assert second_speaker in response.context['speakers']
    assert response.context['search_string'] == search_term
    assert search_term in response


@pytest.mark.django_db
def test_successfully_finds_speaker_by_name_via_search_form(django_app):
    first_speaker = SpeakerFactory(name='Pepito Perez')
    second_speaker = SpeakerFactory(name='Django Pony')
    search_term = 'Pony'
    response = django_app.get(reverse('events:speaker_list'), status=200)

    form = response.forms['speaker_search_form']
    form['q'] = search_term
    response = form.submit()

    assert len(response.context['speakers']) == 1
    assert first_speaker not in response.context['speakers']
    assert second_speaker in response.context['speakers']
    assert response.context['search_string'] == search_term
    assert search_term in response


def test_non_authenticated_user_cannot_create_organizer(django_app):
    response = django_app.get(reverse('events:organizer_add'), status=302)
    assert reverse('users:login') in response.location


@pytest.mark.django_db
def test_non_authenticated_user_cannot_update_organizer(django_app, organizer):
    response = django_app.get(
        reverse('events:organizer_update', args=[organizer.slug]), status=302,
    )
    assert reverse('users:login') in response.location


@pytest.mark.django_db
def test_successfully_create_organizer(django_app, user):
    organizers_count = Organizer.objects.count()

    response = django_app.get(
        reverse('events:organizer_add'),
        user=user,
        status=200,
    )

    form = response.forms['organizer_form']
    form['name'] = 'Librería LERNER'
    form['description'] = 'Librería LERNER'
    form['website_url'] = 'https://www.librerialerner.com.co/'

    response = form.submit()
    assert response.status_code == 302

    assert Organizer.objects.count() == organizers_count + 1

    organizer = Organizer.objects.first()
    assert organizer.created_by == user
    assert organizer.get_absolute_url() in response.location


@pytest.mark.django_db
def test_successfully_update_organizer(django_app, user, organizer):
    organizer.created_by = user
    organizer.save()

    response = django_app.get(
        reverse('events:organizer_update', args=[organizer.slug]),
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


def test_non_authenticated_user_cannot_create_speaker(django_app):
    response = django_app.get(reverse('events:speaker_add'), status=302)
    assert reverse('users:login') in response.location


@pytest.mark.django_db
def test_successfully_create_speaker(django_app, user):
    speakers_count = Speaker.objects.count()

    response = django_app.get(reverse('events:speaker_add'), user=user, status=200)

    form = response.forms['speaker_form']
    form['name'] = 'Julian Barnes'
    form['description'] = 'English writer'

    response = form.submit()
    assert response.status_code == 302

    assert Speaker.objects.count() == speakers_count + 1

    speaker = Speaker.objects.first()
    assert speaker.created_by == user

    assert speaker.get_absolute_url() in response.location

    response = response.follow()
    assert speaker.name in response


@pytest.mark.django_db
def test_non_authenticated_user_cannot_update_speaker(django_app, speaker):
    response = django_app.get(
        reverse('events:speaker_update', args=[speaker.id]), status=302,
    )
    assert reverse('users:login') in response.location


@pytest.mark.django_db
def test_successfully_update_speaker(django_app, user, speaker):
    speaker.created_by = user
    speaker.save()

    response = django_app.get(
        reverse('events:speaker_update', args=[speaker.slug]),
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
