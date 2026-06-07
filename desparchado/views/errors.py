from django.http import HttpResponseForbidden
from django.template import loader

from desparchado.exceptions import UserFacingPermissionDenied


def permission_denied(request, exception):
    """Custom 403 handler that only exposes the exception message for explicitly user-safe exceptions."""
    template = loader.get_template('403.html')
    context = {
        'exception': str(exception) if isinstance(exception, UserFacingPermissionDenied) else '',
    }
    return HttpResponseForbidden(template.render(context, request))
