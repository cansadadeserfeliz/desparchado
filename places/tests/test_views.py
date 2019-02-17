from django.urls import reverse

from django_webtest import WebTest

from .factories import PlaceFactory


class PlaceDetailViewTest(WebTest):

    def setUp(self):
        self.place = PlaceFactory()

    def test_successfully_shows_place(self):
        response = self.app.get(
            reverse('places:place_detail', args=[self.place.slug]),
            status=200
        )
        self.assertEqual(response.context['place'], self.place)
