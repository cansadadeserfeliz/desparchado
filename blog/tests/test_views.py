from django.urls import reverse

from django_webtest import WebTest

from .factories import PostFactory


class PostListViewTest(WebTest):

    def setUp(self):
        self.first_post = PostFactory()
        self.second_post = PostFactory()
        self.not_published_post = PostFactory(is_published=False)
        self.not_approved_post = PostFactory(is_approved=False)

    def test_posts_appear_in_list(self):
        response = self.app.get(reverse('blog:post_list'), status=200)
        self.assertEqual(len(response.context['posts']), 2)
        self.assertIn(self.first_post, response.context['posts'])
        self.assertIn(self.second_post, response.context['posts'])
        self.assertNotIn(self.not_published_post, response.context['posts'])
        self.assertNotIn(self.not_approved_post, response.context['posts'])
