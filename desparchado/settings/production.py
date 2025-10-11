# pylint: disable=unused-wildcard-import
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: F403

DEBUG = False

ALLOWED_HOSTS = ['desparchado.co']

EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'no-reply@desparchado.co'

AXES_IPWARE_META_PRECEDENCE_ORDER = [
    'X-Real-IP',
    'HTTP_X_FORWARDED_FOR',
    'REMOTE_ADDR',
]

DJANGO_VITE['default']['manifest_path'] = STATIC_ROOT / 'dist' / 'manifest.json'   # noqa: F405
DJANGO_VITE['default']['static_url_prefix'] = 'dist'   # noqa: F405

# Sentry
sentry_sdk.init(
    dsn=getenvvar('SENTRY_CONFIG_DNS', 'not-set'),   # noqa: F405
    integrations=[
        DjangoIntegration(),
    ],
    environment='production',
    # Add data like request headers and IP for users;
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/
    # for more info
    send_default_pii=True,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profile_session_sample_rate to 1.0 to profile 100%
    # of profile sessions.
    profile_session_sample_rate=1.0,
    # Set profile_lifecycle to "trace" to automatically
    # run the profiler on when there is an active transaction
    profile_lifecycle="trace",
)

ANALYTICS_ENABLED = True
