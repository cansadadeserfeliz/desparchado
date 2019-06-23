from django.urls import reverse

from django_webtest import WebTest

from .factories import BookFactory


class BookTest(WebTest):

    def setUp(self):
        self.book = BookFactory()

    def test_show_books_list(self):
        self.app.get(reverse('books:book_list'), status=200)

    def test_show_book_detail(self):
        self.app.get(
            reverse('books:book_detail', args=[self.book.slug]),
            status=200
        )
