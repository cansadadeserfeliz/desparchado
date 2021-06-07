import raven
import os

from .base import *


DEBUG = False

ALLOWED_HOSTS = ['*']

EMAIL_USE_TLS = True
EMAIL_ADMIN_USERS = ['desparchado.co@gmail.com']
EMAIL_FROM = 'no-reply@desparchado.co'

RAVEN_CONFIG = {
    'dsn': getenvvar('RAVEN_CONFIG_DNS'),
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
}
