from .base import *

DEBUG = True

STATICFILES_STORAGE = 'pipeline.storage.NonPackagingPipelineStorage'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

PIPELINE['PIPELINE_ENABLED'] = not DEBUG
