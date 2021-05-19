from .base import *

DEBUG = True

STATICFILES_STORAGE = 'pipeline.storage.NonPackagingPipelineStorage'

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

PIPELINE['PIPELINE_ENABLED'] = False
PIPELINE['SASS_BINARY'] = 'sassc'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'desparchado_test',
        'USER': 'desparchado_dev',
        'PASSWORD': 'secret',
        'HOST': 'db',
        'PORT': 5432,
        'TEST': {
            'NAME': 'desparchado_test',
        },
    }
}

LOGGING['root']['handlers'] = ['console']
