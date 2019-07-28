import re
import logging
import requests
from urllib.parse import urljoin

from desparchado.exceptions import RequestFailureException
from desparchado.exceptions import UnknownResultException

logger = logging.getLogger(__name__)


class TagangaClient:
    """
    HTTP client to connect to Taganga.
    """

    def __init__(self, base_url, auth_token, timeout_secs=10):
        """Setting up all the parameters used by the class

        Args:
            base_url (string): Will be used to connect to Taganga
        """
        self.base_url = base_url
        self.timeout_secs = int(timeout_secs)

        self._session = requests.Session()
        self._session.verify = False
        self._session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': 'Token {}'.format(auth_token),
        })

    def _send_http_request(self,
                           path, data, http_verb, headers={},
                           success_statuses=None):
        """Create a payload and send a new post request to the url given

        Args:
            path (string): request endpoint.
            data (dict): a python dict with the body for the request.
            http_verb (string): the type of request you want. Can be either
                'get' or 'post'.
            headers (dict): additional headers
            success_statuses ([int]): a list of HTTP statuses whose response
                the caller wants to handle. Default: [200]. If the response has
                an status code not in this list, RequestFailureException will
                be raised.

        Returns:
            a requests.Response object if the request was succesful. If not, it
            raises either a RequestFailureException (when we got a response,
            and it is not successful according to the list in the
            `success_statuses` argument) or an UnknownResultException if there
            was a network error and we got no response.
        """
        if success_statuses is None:
            success_statuses = [200]

        # so urljoin doesn't discard the base path in base_url if path happens
        # to start with /
        path = re.sub(r'^/+', '', path)

        url = urljoin(self.base_url, path)

        if http_verb not in ['get', 'post', 'put']:
            raise RuntimeError(
                'Programmer error : invalid HTTP request "{}"'.format(http_verb)
            )

        args = dict(
            url=url,
            timeout=self.timeout_secs,
            headers=headers,
        )
        if http_verb == 'get':
            args['params'] = data
        else:  # POST
            args['json'] = data

        debug_info = dict(
            url=url,
            method=http_verb,
            request_body=data,
            timeout_secs=self.timeout_secs,
        )
        try:
            req_func = getattr(self._session, http_verb)
            http_response = req_func(**args)
        except requests.exceptions.ConnectionError as exc:
            logger.error(
                'Could not connect to Taganga API',
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
                'Unknown result in request to Taganga API',
                exc_info=True,
                extra=debug_info,
            )
            raise UnknownResultException(url=url) from exc

        debug_info['response_content'] = http_response.content
        debug_info['response_code'] = http_response.status_code

        if http_response.status_code in success_statuses:
            try:
                json_response = http_response.json()
            except ValueError as exc:
                logger.warning(
                    'Invalid JSON data in Taganga API response',
                    exc_info=True,
                    extra=debug_info,
                )
                raise UnknownResultException(
                    url=url,
                    response=http_response
                ) from exc
            return json_response

        logger.error('Not expected Taganga API response', extra=debug_info)

        if http_response.status_code < 500:
            print('Could not connect', http_response.status_code)
            raise RequestFailureException(url=url, response=http_response)

        raise UnknownResultException(url=url, response=http_response)

    def get(self, path, data,  headers={}, success_statuses=None):
        return self._send_http_request(path, data, 'get', headers, success_statuses)

    def post(self, path, data, headers={}, success_statuses=None):
        return self._send_http_request(path, data, 'post', headers, success_statuses)

    def get_book_prices(self, book_isbn):
        """
        Returns:
            [
               {
                  "slug":"dqzv2kc4pzjdnlmoqp5t",
                  "name":"Mi historia - Michelle Obama",
                  "last_price":59000,
                  "seller_name":"Panamericana",
                  "image_url":"https://panamericana.vteximg.com.br/arquivos/ids/307147-650-650/mi-historia-obama-9789585457188.jpg?v=636789481254770000",
                  "url":"https://www.panamericana.com.co/mi-historia-michelle-obama-563764/p"
               },
               {
                  "slug":"qwxvbhq7e1wehpaywlne",
                  "name":"MI HISTORIA",
                  "last_price":59000,
                  "seller_name":"Librería Nacional",
                  "image_url":"https://crm.librerianacional.com/upload/c3d6a30b-f581-78b6-1ca3-5be70378cca9_imagen",
                  "url":"https://librerianacional.com/producto/365318"
               }
            ]
        """
        http_response = self.get(
            path='item/search',
            data={'isbn': book_isbn},
        )
        print(http_response)
        return http_response
