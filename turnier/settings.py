# -*- coding: utf-8 -*-
"""
Django settings for turnier project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'gltlwaaib01c3!!&ui*7d54fqpu=az1ruv%8tlm$ae@6$rqd*x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'registration',
    'turnier1',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ACCOUNT_ACTIVATION_DAYS=7
#EMAIL_HOST='localhost'
#EMAIL_PORT=1023
#EMAIL_HOST_USER='username'
#EMAIL_HOST_PASSWORD='password'



ROOT_URLCONF = 'turnier.urls'
MEDIA_ROOT    = '/media/'

WSGI_APPLICATION = 'turnier.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'ge-de'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/


STATIC_ROOT = BASE_DIR+'static'
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "turnier/static"),
#    os.path.join(BASE_DIR, "/static/js"),

]


#STATIC_URL  =   [os.path.join(BASE_DIR, 'static')]
#TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]
TEMPLATE_DIRS = [
    os.path.join(BASE_DIR, 'turnier/templates/'),
    #os.path.join(BASE_DIR, 'froff/templates'),
]



