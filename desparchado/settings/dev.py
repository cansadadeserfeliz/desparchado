# pylint: disable=unused-wildcard-import

from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = ['*']

EMAIL_USE_TLS = True
EMAIL_ADMIN_USERS = ['desparchado.co@gmail.com']

AXES_IPWARE_PROXY_COUNT = (
    1  # The number of reverse proxies in front of Django as an integer
)

# django-debug-toolbar
def show_debug_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_debug_toolbar,
}

# Indicates whether to serve assets via the ViteJS development server
# or from compiled production assets
DJANGO_VITE['default']['dev_mode'] = True   # noqa: F405

try:
    from local import *  # noqa: F403
except ModuleNotFoundError:
    pass
