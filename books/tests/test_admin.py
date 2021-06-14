import pytest

from django.urls import reverse

from ..models import Book


@pytest.mark.django_db
def test_show_books_list(django_app, user_admin, book):
    response = django_app.get(
        reverse('admin:books_book_changelist'),
        user=user_admin,
        status=200
    )
    assert book.title in response


@pytest.mark.django_db
def test_add_book(django_app, user_admin, book_author):
    books_count = Book.objects.count()

    response = django_app.get(
        reverse('admin:books_book_add'),
        user=user_admin,
        status=200
    )
    form = response.forms['book_form']
    form['title'] = 'En pos de el dorado. Inmigración japonesa a Colombia'
    form['description'] = 'El libro incluye una selección de 78 fotografías completamente inéditas'
    form['isbn'] = '9789588249339'
    form['authors'].force_value([book_author.id])
    response = form.submit()
    assert response.status_code == 302
    assert Book.objects.count() == books_count + 1


@pytest.mark.django_db
def test_show_authors_list(django_app, user_admin, book_author):
    response = django_app.get(
        reverse('admin:books_author_changelist'),
        user=user_admin,
        status=200
    )
    assert book_author.name in response
