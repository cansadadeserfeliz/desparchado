# pylint: disable=unused-wildcard-import
from .base import *  # noqa: F403

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

LOGGING['root']['handlers'] = ['console']   # noqa: F405

# Indicates whether to serve assets via the ViteJS development server
# or from compiled production assets
DJANGO_VITE['default']['dev_mode'] = True   # noqa: F405
