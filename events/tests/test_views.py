from datetime import timedelta

import pytest

from django.urls import reverse
from django.utils import timezone

from django_webtest import WebTest

from users.tests.factories import UserFactory
from places.tests.factories import PlaceFactory
from .factories import EventFactory
from .factories import OrganizerFactory
from .factories import SpeakerFactory
from ..models import Event
from ..models import Organizer
from ..models import Speaker


@pytest.mark.django_db
def test_events_appearance_in_event_list(django_app, event, not_published_event, not_approved_event, past_event):
    response = django_app.get(reverse('events:event_list'), status=200)

    assert event in response.context['events']
    assert not_published_event not in response.context['events']
    assert not_approved_event not in response.context['events']
    assert past_event not in response.context['events']


@pytest.mark.django_db
def test_show_details_of_event(django_app, event):
    response = django_app.get(
        reverse('events:event_detail', args=[event.slug]),
        status=200
    )
    assert event == response.context['event']


@pytest.mark.django_db
def test_show_book_in_details_of_event(django_app, event, book, other_event):
    response = django_app.get(
        reverse('events:event_detail', args=[event.slug]),
        status=200
    )
    assert book in response.context['books']
    assert book.title in response

    assert other_event not in response.context['books']


@pytest.mark.django_db
def test_show_details_of_not_published_event(django_app, not_published_event):
    django_app.get(
        reverse('events:event_detail', args=[not_published_event.slug]),
        status=404
    )


@pytest.mark.django_db
def test_show_details_of_not_approved_event(django_app, not_approved_event):
    django_app.get(
        reverse('events:event_detail', args=[not_approved_event.slug]),
        status=404
    )


@pytest.mark.django_db
def test_does_not_allow_update_events_not_authenticated_users(django_app, event):
    response = django_app.get(
        reverse('events:event_update', args=[event.id]),
        status=302
    )
    assert reverse('users:login') in response.location


@pytest.mark.django_db
def test_does_not_allow_update_other_users_event(django_app, other_user, event):
    django_app.get(
        reverse('events:event_update', args=[event.id]),
        user=other_user,
        status=403
    )


@pytest.mark.django_db
def test_successfully_update_event(django_app, event_with_organizer):
    event = event_with_organizer
    user = event.created_by
    response = django_app.get(
        reverse('events:event_update', args=[event.id]),
        user=user,
        status=200
    )
    assert event.title in response

    form = response.forms['event_form']
    form['title'] = 'Presentación del libro de Julian Barnes'
    #response = form.submit()
    #print(response)
    form.submit().follow()

    event.refresh_from_db()

    # Title was changed
    assert event.title == 'Presentación del libro de Julian Barnes'


class EventUpdateViewTest(WebTest):

    def setUp(self):
        self.user = UserFactory()
        self.event = EventFactory(created_by=self.user)
        self.event.organizers.add(OrganizerFactory())

    def test_allows_editor_to_edit_event(self):
        editor_user = UserFactory()
        self.event.editors.add(editor_user)

        response = self.app.get(
            reverse('events:event_update', args=[self.event.id]),
            user=editor_user,
            status=200
        )
        self.assertContains(response, self.event.title)

        form = response.forms['event_form']
        form['title'] = 'Presentación del libro de Julian Barnes'
        form.submit().follow()

        self.event.refresh_from_db()

        # Title was changed
        self.assertEqual(self.event.title, 'Presentación del libro de Julian Barnes')
        self.assertEqual(self.event.created_by, self.user)


class OrganizerDetailViewTest(WebTest):

    def setUp(self):
        self.organizer = OrganizerFactory()

    def test_successfully_shows_organizer(self):
        response = self.app.get(
            reverse('events:organizer_detail', args=[self.organizer.slug]),
            status=200
        )
        self.assertEqual(response.context['organizer'], self.organizer)


class SpeakerDetailViewTest(WebTest):

    def setUp(self):
        self.speaker = SpeakerFactory()

    def test_successfully_shows_speaker(self):
        response = self.app.get(
            reverse('events:speaker_detail', args=[self.speaker.slug]),
            status=200
        )
        self.assertEqual(response.context['speaker'], self.speaker)


class SpeakerListViewTest(WebTest):

    def setUp(self):
        self.first_speaker = SpeakerFactory(name='Pepito Perez')
        self.second_speaker = SpeakerFactory(name='Django Pony')

    def test_successfully_shows_speakers_list(self):
        response = self.app.get(reverse('events:speaker_list'), status=200)
        self.assertEqual(len(response.context['speakers']), 2)
        self.assertIn(self.first_speaker, response.context['speakers'])
        self.assertIn(self.second_speaker, response.context['speakers'])

    def test_successfully_finds_speaker_by_name(self):
        search_term = 'Pony'
        response = self.app.get(
            reverse('events:speaker_list'),
            {'q': search_term},
            status=200
        )
        self.assertEqual(len(response.context['speakers']), 1)
        self.assertNotIn(self.first_speaker, response.context['speakers'])
        self.assertIn(self.second_speaker, response.context['speakers'])
        self.assertEqual(response.context['search_string'], search_term)
        self.assertContains(response, search_term)

    def test_successfully_finds_speaker_by_name_via_search_form(self):
        search_term = 'Pony'
        response = self.app.get(reverse('events:speaker_list'), status=200)

        form = response.forms['speaker_search_form']
        form['q'] = search_term
        response = form.submit()

        self.assertEqual(len(response.context['speakers']), 1)
        self.assertNotIn(self.first_speaker, response.context['speakers'])
        self.assertIn(self.second_speaker, response.context['speakers'])
        self.assertEqual(response.context['search_string'], search_term)
        self.assertContains(response, search_term)


class EventCreateViewTest(WebTest):

    def setUp(self):
        self.user = UserFactory()
        self.organizer = OrganizerFactory()
        self.place = PlaceFactory()

    def test_redirects_for_non_authenticated_user(self):
        response = self.app.get(reverse('events:add_event'), status=302)
        self.assertIn(reverse('users:login'), response.location)

    def test_successfully_creates_event(self):
        self.assertEqual(Event.objects.count(), 0)
        response = self.app.get(
            reverse('events:add_event'),
            user=self.user,
            status=200,
        )

        form = response.forms['event_form']

        form['title'] = 'Presentación del libro de Julian Barnes'
        form['description'] = 'Hasta hace poco he visto a Julian Barnes ' \
                              'como uno de esos escritores que nos interesan, ' \
                              'cuya lectura creemos inminente, ' \
                              'pero que vamos aplazando año tras año ' \
                              'sin ningún motivo concreto.'
        form['event_date'] = (
            timezone.now() + timedelta(days=1)
        ).strftime('%d/%m/%Y %H:%M')
        form['event_end_date'] = (
            timezone.now() + timedelta(days=2)
        ).strftime('%d/%m/%Y %H:%M')
        form['event_source_url'] = 'http://example.com'
        form['organizers'].force_value([self.organizer.id])
        form['place'].force_value(self.place.id)

        response = form.submit().follow()

        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.first()
        self.assertEqual(event.created_by, self.user)


class OrganizerCreateViewTest(WebTest):

    def setUp(self):
        self.user = UserFactory()

    def test_redirects_for_non_authenticated_user(self):
        response = self.app.get(reverse('events:organizer_add'), status=302)
        self.assertIn(reverse('users:login'), response.location)

    def test_successfully_creates_organizer(self):
        self.assertEqual(Organizer.objects.count(), 0)

        response = self.app.get(
            reverse('events:organizer_add'),
            user=self.user,
            status=200,
        )

        form = response.forms['organizer_form']
        form['name'] = 'Librería LERNER'
        form['description'] = 'Librería LERNER'
        form['website_url'] = 'https://www.librerialerner.com.co/'

        response = form.submit().follow()

        self.assertEqual(Organizer.objects.count(), 1)

        organizer = Organizer.objects.first()
        self.assertEqual(organizer.created_by, self.user)


class OrganizerUpdateViewTest(WebTest):

    def setUp(self):
        self.user = UserFactory()
        self.organizer = OrganizerFactory(
            name='Librería LERNER',
            created_by=self.user,
        )

    def test_redirects_for_non_authenticated_user(self):
        response = self.app.get(
            reverse('events:organizer_update', args=[self.organizer.slug]),
            status=302
        )
        self.assertIn(reverse('users:login'), response.location)

    def test_successfully_updates_organizer(self):
        response = self.app.get(
            reverse('events:organizer_update', args=[self.organizer.slug]),
            user=self.user,
            status=200,
        )

        form = response.forms['organizer_form']
        form['name'] = 'Librería Nacional'

        response = form.submit().follow()

        self.organizer.refresh_from_db()

        self.assertEqual(self.organizer.created_by, self.user)
        self.assertEqual(self.organizer.name, 'Librería Nacional')


class SpeakerCreateViewTest(WebTest):

    def setUp(self):
        self.user = UserFactory()

    def test_redirects_for_non_authenticated_user(self):
        response = self.app.get(reverse('events:speaker_add'), status=302)
        self.assertIn(reverse('users:login'), response.location)

    def test_successfully_creates_speaker(self):
        self.assertEqual(Speaker.objects.count(), 0)

        response = self.app.get(
            reverse('events:speaker_add'),
            user=self.user,
            status=200,
        )

        form = response.forms['speaker_form']
        form['name'] = 'Julian Barnes'
        form['description'] = 'English writer'

        response = form.submit().follow()

        self.assertEqual(Speaker.objects.count(), 1)

        speaker = Speaker.objects.first()
        self.assertEqual(speaker.created_by, self.user)

        self.assertContains(response, speaker.name)


class SpeakerUpdateViewTest(WebTest):

    def setUp(self):
        self.user = UserFactory()
        self.speaker = SpeakerFactory(
            name='Julian Barnes',
            created_by=self.user,
        )

    def test_redirects_for_non_authenticated_user(self):
        response = self.app.get(
            reverse('events:speaker_update', args=[self.speaker.id]),
            status=302
        )
        self.assertIn(reverse('users:login'), response.location)

    def test_successfully_updates_speaker(self):
        response = self.app.get(
            reverse('events:speaker_update', args=[self.speaker.slug]),
            user=self.user,
            status=200,
        )

        form = response.forms['speaker_form']
        form['name'] = 'Chimamanda Ngozi Adichie'

        response = form.submit().follow()

        self.speaker.refresh_from_db()

        self.assertEqual(self.speaker.created_by, self.user)
        self.assertEqual(self.speaker.name, 'Chimamanda Ngozi Adichie')
