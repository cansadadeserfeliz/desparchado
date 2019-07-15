from django_webtest import WebTest

from .


class GoodreadsService(WebTest):

    def test_get_book_info(self):
        response = self.app.get(reverse('home'), status=200)
        self.assertContains(response, 'AÑADIR EVENTO')
