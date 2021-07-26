import os
from pathlib import Path

from django.urls import reverse_lazy
from django.core.exceptions import ImproperlyConfigured


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
    'markdownx',
    'mapwidgets',
    'pipeline',
    'raven.contrib.django.raven_compat',
    'social_django',
    'crispy_forms',
    'crispy_bootstrap5',
    'debug_toolbar',

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
    'social_core.backends.facebook.FacebookOAuth2',

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

                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
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

LANGUAGE_CODE = 'es-CO'
LANGUAGES = [
    ('es-CO', 'Español'),
]

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_L10N = True

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

    'pipeline.finders.FileSystemFinder',
    'pipeline.finders.AppDirectoriesFinder',
    'pipeline.finders.CachedFileFinder',
    'pipeline.finders.PipelineFinder',
)

SITE_ID = 1

# django-pipeline
STATICFILES_STORAGE = 'pipeline.storage.PipelineManifestStorage'
PIPELINE = {
    'COMPILERS': (
        'pipeline.compilers.sass.SASSCompiler',
    ),
    'JS_COMPRESSOR': None,
    'STYLESHEETS': {
        'main': {
            'source_filenames': (
              #'bower_components/bootstrap/dist/css/bootstrap.min.css',
              #'libs/fontawesome-free-5.6.3-web/css/all.min.css',
              #'bower_components/tempusdominus-bootstrap-4/build/css/tempusdominus-bootstrap-4.min.css',
              'sass/main.sass',
            ),
            'output_filename': 'css/main.min.css',
        },
        'admin': {
            'source_filenames': (
              'sass/dashboard.sass',
            ),
            'output_filename': 'css/admin.min.css',
        },
        'dashboard': {
            'source_filenames': (
              #'bower_components/bootstrap/dist/css/bootstrap.min.css',
              #'libs/fontawesome-free-5.6.3-web/css/all.min.css',
              #'bower_components/Ionicons/css/ionicons.min.css',
              #'bower_components/fullcalendar/dist/fullcalendar.min.css',
              'sass/dashboard.sass',
            ),
            'output_filename': 'css/dashboard.min.css',
        },
    },
    'JAVASCRIPT': {
        'main': {
            'source_filenames': (
              #'bower_components/jquery/dist/jquery.min.js',
              #'bower_components/bootstrap/dist/js/bootstrap.min.js',
              #'bower_components/moment/min/moment-with-locales.min.js',
              #'bower_components/tempusdominus-bootstrap-4/build/js/tempusdominus-bootstrap-4.min.js',
              'js/main.js',
              'js/letter-avatars.js',
              'js/posts-pagination-initializer.js',
            ),
            'output_filename': 'js/main.min.js',
        },
        'dashboard': {
            'source_filenames': (
              #'bower_components/jquery/dist/jquery.min.js',
              #'bower_components/bootstrap/dist/js/bootstrap.min.js',
              #'bower_components/moment/min/moment-with-locales.min.js',
              #'bower_components/jquery-slimscroll/jquery.slimscroll.min.js',
              #'bower_components/fastclick/lib/fastclick.js',
              #'bower_components/fullcalendar/dist/fullcalendar.min.js',
              'js/dashboard.js',
            ),
            'output_filename': 'js/dashboard.min.js',
        },
    },
}

RAVEN_CONFIG = {
    'dsn': 'https://secretuser:secretpassword@sentry.io/secretid',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry', 'console'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'INFO',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

# django-axes
AXES_LOGIN_FAILURE_LIMIT = 5

GOOGLE_ANALYTICS_CODE = 'UA-43471959-4'

# crispy forms with bootstrap 5: https://github.com/django-crispy-forms/crispy-bootstrap5
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)
SOCIAL_AUTH_FACEBOOK_KEY = getenvvar('SOCIAL_AUTH_FACEBOOK_KEY', 'not-set')
SOCIAL_AUTH_FACEBOOK_SECRET = getenvvar('SOCIAL_AUTH_FACEBOOK_SECRET', 'not-set')

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'

SOCIAL_AUTH_FACEBOOK_IGNORE_DEFAULT_SCOPE = True
SOCIAL_AUTH_FACEBOOK_SCOPE = [
    'email'
]

GOODREADS_API_KEY = getenvvar('GOODREADS_API_KEY', 'not-set')
GOODREADS_API_SECRET = getenvvar('GOODREADS_API_SECRET', 'not-set')

TAGANGA_AUTH_TOKEN = getenvvar('TAGANGA_AUTH_TOKEN', 'not-set')
TAGANGA_BASE_URL = 'https://taganga-api.herokuapp.com/api/v1/'

MAP_WIDGETS = {
    "GooglePointFieldWidget": (
        ("zoom", 12),
        ("mapCenterLocation", [4.5930632, -74.0757637]),
        ("mapCenterLocationName", "bogota"),
        ("language", 'es'),
    ),
    "GOOGLE_MAP_API_KEY": 'AIzaSyAFbA9J0IcGyy20cl7xd6Le16U_Bx_TSeI',
    "LANGUAGE": 'es',
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

MARKDOWNX_MARKDOWN_EXTENSIONS = [
    'markdown.extensions.extra'
]
