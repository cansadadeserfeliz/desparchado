# pylint: disable=unused-wildcard-import
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = ['*']

EMAIL_USE_TLS = True
EMAIL_ADMIN_USERS = ['desparchado.co@gmail.com']


# django-debug-toolbar
def show_debug_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_debug_toolbar,
}

# Indicates whether to serve assets via the ViteJS development server
# or from compiled production assets
DJANGO_VITE['default']['dev_mode'] = True   # noqa: F405
