from datetime import timedelta

from django.core.urlresolvers import reverse
from django.utils import timezone

from django_webtest import WebTest

from .factories import EventFactory
from .factories import OrganizerFactory
from .factories import SpeakerFactory


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
