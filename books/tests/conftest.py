import pytest

from .factories import AuthorFactory


@pytest.fixture
def book_author():
    return AuthorFactory()
