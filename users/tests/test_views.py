from django.core.urlresolvers import reverse

from django_webtest import WebTest

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
