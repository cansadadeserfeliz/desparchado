STATICFILES_STORAGE = 'pipeline.storage.NonPackagingPipelineStorage'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'test_desparchado',
        'USER': 'vero4ka',
        'PASSWORD': 'secret',
        'HOST': '127.0.0.1',
        'PORT': '5434',
    }
}
