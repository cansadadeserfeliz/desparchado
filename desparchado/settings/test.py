from .base import *

DEBUG = True

STATICFILES_STORAGE = 'pipeline.storage.NonPackagingPipelineStorage'

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

PIPELINE['PIPELINE_ENABLED'] = not DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'test_desparchado',
        'USER': 'vero4ka',
        'PASSWORD': 'secret',
        'HOST': 'db',
        'PORT': 5432,
    }
}