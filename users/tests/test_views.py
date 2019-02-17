from django.urls import reverse

from django_webtest import WebTest

from events.tests.factories import EventFactory
from .factories import UserFactory


class UserDetailViewTest(WebTest):

    def setUp(self):
        self.authenticated_user = UserFactory()
        self.user = UserFactory()

    def test_successfully_shows_user(self):
        response = self.app.get(
            reverse('users:user_detail', args=[self.user.username]),
            status=200
        )
        self.assertEqual(response.context['user_object'], self.user)
        self.assertContains(response, self.user.first_name)

    def test_successfully_shows_user_detail_for_authenticated_user(self):
        response = self.app.get(
            reverse('users:user_detail', args=[self.user.username]),
            user=self.authenticated_user,
            status=200
        )
        self.assertEqual(response.context['user_object'], self.user)
        self.assertContains(response, self.user.first_name)


class UserAddedEventsListViewTest(WebTest):

    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()

        self.first_event = EventFactory(created_by=self.user)
        self.second_event = EventFactory(created_by=self.user)

        self.other_user_event = EventFactory(
            created_by=self.other_user
        )

    def test_redirects_for_non_authenticated_user(self):
        response = self.app.get(
            reverse('users:user_added_events_list'),
            status=302
        )
        self.assertIn(reverse('users:login'), response.location)

    def test_successfully_shows_user_events(self):
        response = self.app.get(
            reverse('users:user_added_events_list'),
            user=self.user,
            status=200
        )

        self.assertEqual(response.context['user_object'], self.user)
        self.assertEqual(len(response.context['events']), 2)
        self.assertIn(self.first_event, response.context['events'])
        self.assertIn(self.second_event, response.context['events'])
        self.assertNotIn(self.other_user_event, response.context['events'])
