from .base import *

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

LOGGING['root']['handlers'] = ['console']
