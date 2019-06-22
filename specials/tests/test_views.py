from django.urls import reverse

from django_webtest import WebTest

from events.tests.factories import EventFactory
from .factories import SpecialFactory


class SpecialDetailViewTest(WebTest):

    def test_successfully_shows_special(self):
        special = SpecialFactory(related_events=[EventFactory()])
        response = self.app.get(
            reverse('specials:special_detail', args=[special.slug]),
            status=200
        )
        self.assertEqual(response.context['special'], special)

    def test_does_not_show_not_published_event(self):
        not_published_special = SpecialFactory(is_published=False)
        self.app.get(
            reverse('specials:special_detail', args=[not_published_special.slug]),
            status=404
        )
