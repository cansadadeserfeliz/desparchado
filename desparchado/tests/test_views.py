from django.core.urlresolvers import reverse

from django_webtest import WebTest


class HomeViewTestCase(WebTest):

    def testBlog(self):
        response = self.app.get(reverse('home'), status=200)
        self.assertContains(response, 'Eventos para usted')


class AboutViewTestCase(WebTest):

    def testBlog(self):
        self.app.get(reverse('about'), status=200)
