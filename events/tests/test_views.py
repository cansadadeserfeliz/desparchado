from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from django_webtest import WebTest

from books.tests.factories import BookFactory
from users.tests.factories import UserFactory
from places.tests.factories import PlaceFactory
from .factories import EventFactory
from .factories import OrganizerFactory
from .factories import SpeakerFactory
from ..models import Event
from ..models import Organizer
from ..models import Speaker


class EventListViewTest(WebTest):

    def setUp(self):
        self.first_event = EventFactory()
        self.second_event = EventFactory()
        self.not_published_event = EventFactory(is_published=False)
        self.not_approved_event = EventFactory(is_approved=False)
        self.past_event = EventFactory(
            event_date=timezone.now() - timedelta(days=1)
        )

    def test_events_appear_in_list(self):
        response = self.app.get(reverse('events:event_list'), status=200)
        self.assertEqual(len(response.context['events']), 2)
        self.assertIn(self.first_event, response.context['events'])
        self.assertIn(self.second_event, response.context['events'])
        self.assertNotIn(self.not_published_event, response.context['events'])
        self.assertNotIn(self.not_approved_event, response.context['events'])
        self.assertNotIn(self.past_event, response.context['events'])


class EventDetailViewTest(WebTest):

    def test_successfully_shows_event(self):
        event = EventFactory()
        BookFactory(related_events=[event])
        response = self.app.get(
            reverse('events:event_detail', args=[event.slug]),
            status=200
        )
        self.assertEqual(response.context['event'], event)

    def test_does_not_show_not_published_event(self):
        not_published_event = EventFactory(is_published=False)
        self.app.get(
            reverse('events:event_detail', args=[not_published_event.slug]),
            status=404
        )

    def test_does_not_show_not_approved_event(self):
        not_approved_event = EventFactory(is_approved=False)
        self.app.get(
            reverse('events:event_detail', args=[not_approved_event.slug]),
            status=404
        )


class EventUpdateViewTest(WebTest):

    def setUp(self):
        self.user = UserFactory()
        self.event = EventFactory(created_by=self.user)
        self.event.organizers.add(OrganizerFactory())

    def test_redirects_for_non_authenticated_user(self):
        response = self.app.get(
            reverse('events:event_update', args=[self.event.id]),
            status=302
        )
        self.assertIn(reverse('users:login'), response.location)

    def test_redirects_for_not_event_creator(self):
        user = UserFactory()
        self.app.get(
            reverse('events:event_update', args=[self.event.id]),
            user=user,
            status=403
        )


    def test_successfully_updates_event(self):
        response = self.app.get(
            reverse('events:event_update', args=[self.event.id]),
            user=self.user,
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
