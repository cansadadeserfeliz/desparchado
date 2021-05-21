from .base import *

DEBUG = True

STATICFILES_STORAGE = 'pipeline.storage.NonPackagingPipelineStorage'

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

PIPELINE['PIPELINE_ENABLED'] = False
PIPELINE['SASS_BINARY'] = 'sassc'

LOGGING['root']['handlers'] = ['console']
