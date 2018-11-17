from django.core.urlresolvers import reverse

from django_webtest import WebTest


class EventListView(WebTest):

    def testBlog(self):
        response = self.app.get(reverse('events:event_list'), status=200)
        print(response.context)
        self.assertEqual(len(response.context['events']), 0)
