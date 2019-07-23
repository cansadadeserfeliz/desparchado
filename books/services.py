import logging

from django.conf import settings

from .goodreads_client import GoodreadsClient
from .goodreads_client import RequestFailureException
from .goodreads_client import UnknownResultException

logger = logging.getLogger(__name__)


def get_goodreads_client(timeout_secs=10):
    return GoodreadsClient(
        developer_key=settings.GOODREADS_API_KEY,
        timeout_secs=timeout_secs,
    )


def goodreads_search_book(search_string):
    goodreads_client = get_goodreads_client(timeout_secs=10)
    try:
        response_data = goodreads_client.search_book(search_string)
    except RequestFailureException:
        return None
    except UnknownResultException:
        return None

    return response_data


def goodreads_get_book_info(book_isbn):
    goodreads_client = get_goodreads_client(timeout_secs=10)
    try:
        root = goodreads_client.get_book_info(book_isbn)
    except (RequestFailureException, UnknownResultException):
        return None

    book_data = root.find('book')

    return dict(
        title=book_data.find('title').text,
        description=book_data.find('description').text,
        image_url=book_data.find('image_url').text,
        url=book_data.find('url').text,
        average_rating=book_data.find('average_rating').text,
        ratings_count=book_data.find('ratings_count').text,
    )

