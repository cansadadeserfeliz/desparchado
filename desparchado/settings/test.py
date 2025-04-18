from .base import *

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

LOGGING['root']['handlers'] = ['console']

# Indicates whether to serve assets via the ViteJS development server
# or from compiled production assets
DJANGO_VITE['default']['dev_mode'] = True
