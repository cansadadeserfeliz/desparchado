import os

from .base import *

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


DEBUG = False

ALLOWED_HOSTS = ['*']

EMAIL_USE_TLS = True
EMAIL_ADMIN_USERS = ['desparchado.co@gmail.com']
EMAIL_FROM = 'no-reply@desparchado.co'


# Sentry
sentry_sdk.init(
    dsn=getenvvar('SENTRY_CONFIG_DNS', 'not-set'),
    integrations=[
        DjangoIntegration(),
    ],
    environment='production',
    # Add data like request headers and IP for users;
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)
