from .base import *

DEBUG = True

PIPELINE['PIPELINE_ENABLED'] = not DEBUG
PIPELINE['SASS_BINARY'] = 'sassc'

ALLOWED_HOSTS = ['*']

EMAIL_USE_TLS = True
EMAIL_ADMIN_USERS = ['desparchado.co@gmail.com']


# django-debug-toolbar
def show_debug_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_debug_toolbar,
}
