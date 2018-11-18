import datetime
from datetime import timedelta

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from .factories import EventFactory
from ..models import Event


class EventListView(WebTest):

    def setUp(self):
        self.first_event = EventFactory()
        self.second_event = EventFactory()
        self.not_published_event = EventFactory(is_published=False)
        self.not_approved_event = EventFactory(is_approved=False)
        self.past_event = EventFactory(
            event_date=datetime.datetime.now() - timedelta(days=1)
        )

    def test_events_appear_in_list(self):
        response = self.app.get(reverse('events:event_list'), status=200)
        self.assertEqual(len(response.context['events']), 2)
        self.assertIn(self.first_event, response.context['events'])
        self.assertIn(self.second_event, response.context['events'])
        self.assertNotIn(self.not_published_event, response.context['events'])
        self.assertNotIn(self.not_approved_event, response.context['events'])
        self.assertNotIn(self.past_event, response.context['events'])


class EventDetailView(WebTest):

    def setUp(self):
        self.event = EventFactory()

    def test_successfully_shows_event(self):
        response = self.app.get(
            reverse('events:event_detail', args=[self.event.slug]),
            status=200
        )
        self.assertEqual(response.context['event'], self.event)


