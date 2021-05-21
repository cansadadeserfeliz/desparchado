import pytest

from django.urls import reverse


@pytest.mark.django_db
def test_show_home_view(django_app, book):
    response = django_app.get(reverse('books:home'), status=200)
    assert book.title in response


@pytest.mark.django_db
def test_show_book_list(django_app, book):
    response = django_app.get(reverse('books:book_list'), status=200)
    assert book.title in response


@pytest.mark.django_db
def test_show_book_detail(django_app, book):
    response = django_app.get(reverse('books:book_detail', args=[book.slug]), status=200)
    assert book.title in response

