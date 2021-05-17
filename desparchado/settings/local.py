from .base import *

DEBUG = True

PIPELINE['PIPELINE_ENABLED'] = not DEBUG
PIPELINE['SASS_BINARY'] = 'sassc'

ALLOWED_HOSTS = ['*']

EMAIL_USE_TLS = True
EMAIL_ADMIN_USERS = ['vero4ka.ru@gmail.com']

AXES_ENABLED = False
