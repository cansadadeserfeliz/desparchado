import logging

from django.http import HttpRequest, HttpResponseForbidden
from django.template import loader

from desparchado.exceptions import UserFacingPermissionDenied

logger = logging.getLogger(__name__)


def permission_denied(
    request: HttpRequest, exception: Exception,
) -> HttpResponseForbidden:
    """Custom 403 handler.

    Exposes the exception message only for explicitly user-safe exceptions.

    Args:
        request: The current HTTP request.
        exception: The exception that triggered the 403.

    Returns:
        HttpResponseForbidden rendered with the 403 template.
    """
    template = loader.get_template('403.html')
    if isinstance(exception, UserFacingPermissionDenied):
        message = str(exception)
    else:
        logger.warning('Permission denied (not user-facing): %s', exception)
        message = ''
    context = {'exception': message}
    return HttpResponseForbidden(template.render(context, request))
