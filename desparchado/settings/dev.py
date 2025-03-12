from .base import *

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


DEBUG = True

PIPELINE['PIPELINE_ENABLED'] = not DEBUG
PIPELINE['SASS_BINARY'] = 'sassc'

ALLOWED_HOSTS = ['*']

EMAIL_USE_TLS = True
EMAIL_ADMIN_USERS = ['desparchado.co@gmail.com']


# django-debug-toolbar
def show_debug_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_debug_toolbar,
}

# Sentry
sentry_sdk.init(
    dsn=getenvvar('SENTRY_CONFIG_DNS', 'not-set'),
    integrations=[
        DjangoIntegration(),
    ],
    environment='development',
    # Add data like request headers and IP for users;
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)
