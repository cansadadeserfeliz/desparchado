from django.core.urlresolvers import reverse

from django_webtest import WebTest

from .factories import EventFactory
from ..models import Event


class EventListView(WebTest):

    def setUp(self):
        self.first_event = EventFactory()
        self.second_event = EventFactory()
        self.unpublished_event = EventFactory(is_published=False)

    def testBlog(self):
        response = self.app.get(reverse('events:event_list'), status=200)
        self.assertEqual(len(response.context['events']), 2)
        self.assertIn(self.first_event, response.context['events'])
