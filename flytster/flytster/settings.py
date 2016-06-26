"""
Django settings for flytster project.

Generated by 'django-admin startproject' using Django 1.9.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import sys
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv('SECRET_KEY', None)
assert SECRET_KEY

DEBUG = True if os.getenv('DEBUG') == 'True' else False

TESTING = 'test' in sys.argv

ALLOWED_HOSTS = ['*']

AUTH_USER_MODEL = 'users.FlytsterUser'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'authentication',
    'credits',
    'passengers',
    'trips',
    'users',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'authentication.models.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'NON_FIELD_ERRORS_KEY': 'detail',
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S.%fZ',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'flytster.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'flytster.wsgi.application'


# Database
LOCAL_DB_IP = os.environ.get('DB_1_PORT_5432_TCP_ADDR')

DATABASES = {
    'default': dj_database_url.config(
        default='postgres://postgres:postgres@{0}/postgres'.format(LOCAL_DB_IP)
    )
}

# DB_URL = os.getenv('DATABASE_URL', 'postgres://postgres:postgres@{0}/postgres'.format(
#     os.getenv('DB_1_PORT_5432_TCP_ADDR')))
#
# DATABASES = {
#     'default': dj_database_url.config(default=DB_URL)
# }


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

# Application constants
FLYTSTER_API_URL = 'http://192.168.99.100:8000'
AUTH_TOKEN_EXP_IN_DAYS = 7
VERIFICATION_TOKEN_EXP_IN_DAYS = 7
USER_CREDIT_EXP_IN_DAYS = 365

# Flytster info
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', None)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', None)

# Google API
QPX_SERVER_KEY = os.getenv('QPX_SERVER_KEY', None)
GOOGLE_TRIP_SEARCH_URL = 'https://www.googleapis.com/qpxExpress/v1/trips/search'

# Twilio API
TWILIO_ACCOUNT_ID = os.getenv('TWILIO_ACCOUNT_ID')
TWILIO_API_TOKEN = os.getenv('TWILIO_API_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')

# Sabre API
SABRE_TESTING_URL = "https://sws3-crt.cert.sabre.com"
SABRE_PRODUCTION_URL = "https://webservices3.sabre.com"
SABRE_USERNAME = os.getenv('SABRE_USERNAME', None)
SABRE_PASSWORD = os.getenv('SABRE_PASSWORD', None)
