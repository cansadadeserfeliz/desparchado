import os
from pathlib import Path

from django.urls import reverse_lazy
from django.core.exceptions import ImproperlyConfigured

from dotenv import load_dotenv

load_dotenv()  # set environment variables from the .env file


def getenvvar(name, default=None):
    v = os.environ.get(name, default)
    if not v:
        raise ImproperlyConfigured('Set the {} environment variable'.format(name))
    return v


BASE_DIR = Path('.').parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenvvar('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

DEFAULT_AUTO_FIELD='django.db.models.AutoField'

# Application definition

INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'desparchado',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.gis',
    'django.contrib.humanize',
    'django.contrib.postgres',

    'axes',
    'mapwidgets',
    'crispy_forms',
    'crispy_bootstrap5',
    'debug_toolbar',
    'django_vite',
    'drf_yasg',
    'django_filters',
    'rest_framework',

    'dashboard',
    'events',
    'places',
    'users',
    'blog',
    'games',
    'specials',
    'books',
    'news',
    'history',
    'playground',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'axes.middleware.AxesMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
]

ABSOLUTE_URL_OVERRIDES = {
    'users.user_detail': lambda o: "/users/%s/" % o.username,
}

ROOT_URLCONF = 'desparchado.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'desparchado.template.context_processors.constants',
            ],
        },
    },
]

WSGI_APPLICATION = 'desparchado.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': getenvvar('DATABASE_NAME'),
        'USER': getenvvar('DATABASE_USER'),
        'PASSWORD': getenvvar('DATABASE_PASSWORD'),
        'HOST': getenvvar('DATABASE_HOST'),
        'PORT': getenvvar('DATABASE_PORT'),
        'TEST': {
            'NAME': 'desparchado_test',
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGIN_URL = reverse_lazy('users:login')
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

USE_I18N = True
LANGUAGE_CODE = 'es-CO'
LANGUAGES = [
    ('es-CO', 'Español'),
]

TIME_ZONE = 'America/Bogota'
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = BASE_DIR / 'static'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS = [
    BASE_DIR / 'desparchado/static',
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SITE_ID = 1

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
}

# Brute force login attacks: django-axes
AXES_FAILURE_LIMIT = 5
# defines a period of inactivity after which old failed login attempts will be cleared
AXES_COOLOFF_TIME = 24  # hours
AXES_IPWARE_PROXY_COUNT = 1  # The number of reverse proxies in front of Django as an integer
AXES_IPWARE_META_PRECEDENCE_ORDER = [
    'HTTP_X_FORWARDED_FOR',
    'REMOTE_ADDR',
]

# crispy forms with bootstrap 5:
# https://github.com/django-crispy-forms/crispy-bootstrap5
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

GOOGLE_MAPS_API_KEY = getenvvar('GOOGLE_MAPS_API_KEY', 'not-set')
MAP_WIDGETS = {
    "GoogleMap": {
        "apiKey": GOOGLE_MAPS_API_KEY,
        "CDNURLParams": {
            "language": "es",
            "libraries": "places,marker",
            "loading": "async",
            "v": "quarterly",
        },
        "PointField": {
            "interactive": {
                "mapOptions": {
                    "zoom": 5,  # default map initial zoom,
                    "scrollwheel": False,
                    "streetViewControl": True
                },
                "GooglePlaceAutocompleteOptions": {
                    "componentRestrictions": {"country": "co"}
                },
                "mapCenterLocationName": "Bogota"
            },
        },
    },
}


EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django_ses.SESBackend'
EMAIL_FROM = 'no-reply@desparchado.co'

AWS_SES_ACCESS_KEY_ID = getenvvar('AWS_SES_ACCESS_KEY_ID', 'not-set')
AWS_SES_SECRET_ACCESS_KEY = getenvvar('AWS_SES_SECRET_ACCESS_KEY', 'not-set')
AWS_ACCESS_KEY_ID = getenvvar('AWS_SES_ACCESS_KEY_ID', 'not-set')
AWS_SECRET_ACCESS_KEY = getenvvar('AWS_SES_SECRET_ACCESS_KEY', 'not-set')

AWS_SES_REGION_NAME = 'us-east-1'
AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'

# django-debug-toolbar
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# django-vite
DJANGO_VITE = {
  'default': {
    'dev_mode': False,
  }
}

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
}
