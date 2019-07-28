class RequestFailureException(Exception):
    """Raised when the request did *not* succeed, and we know nothing happened
    in the remote side. From a business-logic point of view, the operation the
    client was supposed to perform did NOT happen"""

    def __init__(self, *args, url='', response=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.response = response
        self.url = url


class UnknownResultException(Exception):
    """Raised when we don't know if the request was completed or not. From a
    business-logic point of view, it is not known if the operation succeeded,
    or failed"""

    def __init__(self, *args, url='', response=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.response = response
        self.url = url
