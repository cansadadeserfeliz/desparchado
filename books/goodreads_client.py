import re
import logging
import requests
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

from desparchado.exceptions import RequestFailureException
from desparchado.exceptions import UnknownResultException


logger = logging.getLogger(__name__)


class GoodreadsClient:
    """HTTP client to connect to Goodreads."""

    def __init__(self, developer_key, timeout_secs=10):
        """Setting up all the parameters used by the class

        Args:
            base_url (string): Will be used to connect to Goodreads
        """
        self.base_url = 'https://www.goodreads.com/'
        self.timeout_secs = int(timeout_secs)
        self.developer_key = developer_key

        self._session = requests.Session()
        self._session.verify = False
        self._session.headers.update({
            'Content-Type': 'application/json',
        })

    def _send_get_request(self, path, data, success_statuses=None):
        if success_statuses is None:
            success_statuses = [200]

        # so urljoin doesn't discard the base path in base_url if path happens
        # to start with /
        path = re.sub(r'^/+', '', path)

        url = urljoin(self.base_url, path)
        data.update({'key': self.developer_key})
        debug_info = dict(
            url=url,
            request_body=data,
            timeout_secs=self.timeout_secs,
        )
        try:
            http_response = requests.get(url, data=data, timeout=self.timeout_secs)
        except requests.exceptions.ConnectionError as exc:
            logger.error(
                'Could not connect to Goodreads API',
                exc_info=True,
                extra=debug_info,
            )
            raise RequestFailureException(url=url) from exc
        except (
            requests.exceptions.Timeout,
            requests.exceptions.ReadTimeout,
            requests.exceptions.RequestException,
        ) as exc:
            logger.error(
                'Unknown result in request to Goodreads API',
                exc_info=True,
                extra=debug_info,
            )
            raise UnknownResultException(url=url) from exc

        debug_info['response_content'] = http_response.content
        debug_info['response_code'] = http_response.status_code

        logger.error('Not expected Goodreads response', extra=debug_info)

        if http_response.status_code in success_statuses:
            try:
                root = ET.fromstring(http_response.content)
            except (ValueError, ET.ParseError) as exc:
                logger.warning(
                    'Invalid XML data in Goodreads response',
                    exc_info=True,
                    extra=debug_info,
                )
                raise UnknownResultException(
                    url=url,
                    response=http_response
                ) from exc

            return root

        if http_response.status_code < 500:
            raise RequestFailureException(url=url, response=http_response)

        raise UnknownResultException(url=url, response=http_response)

    def search_book(self, search_string):

        http_response = self.get(
            path='search/index.xml',
            data={
                'q': search_string,
            },
        )
        return http_response

    def get_book_info(self, book_isbn):

        http_response = self._send_get_request(
            path='book/isbn/{}'.format(book_isbn),
            data={},
        )
        return http_response
