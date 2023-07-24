"""
Django settings for djangoProject project.

Generated by 'django-admin_panel startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
import sys
from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG') == 'True'

ALLOWED_HOSTS = env('ALLOWED_HOSTS').split(',')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'debug_toolbar',
    'crispy_forms',
    'crispy_bootstrap5',
    'main_page',
    'account.apps.AuthConfig',
    'city',
    'news',
    'region',
    'collection',
    'mathfilters',
    'mdeditor',
    'markdownify'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'MoiGoroda.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'MoiGoroda.context_processors.general_settings'
            ],
        },
    },
]

WSGI_APPLICATION = 'MoiGoroda.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT')
    }
}

if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mydatabase'
    }

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
STATIC_ROOT = env('STATIC_ROOT')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = 'bootstrap5'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

INTERNAL_IPS = [
    '127.0.0.1', '0.0.0.0'
]

LOGIN_URL = '/account/signin'

EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = env('EMAIL_USE_TLS') == 'True'
EMAIL_USE_SSL = env('EMAIL_USE_SSL') == 'True'

SERVER_EMAIL = env('SERVER_EMAIL')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
ADMINS = [(env('ADMIN_NAME'), env('ADMIN_EMAIL')), ]

LOG_FIlE_PATH = os.path.join(BASE_DIR, 'logs/log.log')
if not os.path.exists(os.path.dirname(LOG_FIlE_PATH)):
    os.mkdir(os.path.dirname(LOG_FIlE_PATH))
if not os.path.exists(LOG_FIlE_PATH):
    open(LOG_FIlE_PATH, 'a').close()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        # Отправка писем только при DEBUG = False
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },

    'formatters': {
        'file': {
            'format': '%(levelname)-8s %(asctime)-25s %(filename)-20s %(funcName)-25s %(lineno)-7d %(message)s'
        }
    },

    'handlers': {
        # Запись сообщения в файл
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': LOG_FIlE_PATH
        },
        # Отправка письма на почту
        'email': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,

        },
        # Отправка письма на почту
        'email_signup': {
            'level': 'INFO',
            # 'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,

        }
    },

    'loggers': {
        'moi-goroda': {
            'handlers': ['file', 'email'],
            'level': 'INFO',
            'propogate': True
        },
        'account.views': {
            'handlers': ['file', 'email_signup'],
            'level': 'INFO',
            'propogate': True
        },
        'django': {
            'level': 'WARNING',
            'handlers': ['file', 'email']
        }
    }
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# MDEditor
X_FRAME_OPTIONS = 'SAMEORIGIN'
MDEDITOR_CONFIGS = {
    'default': {
        'language': 'en'
    }
}

# Markdownify
MARKDOWNIFY = {
    "default": {
        'WHITELIST_TAGS': [
            # Протестированные теги
            'a', 'blockquote', 'code', 'img', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong',
            # Непротестированные теги
            'li', 'ol', 'p', 'ul'],
        'WHITELIST_ATTRS': ['href', 'src', 'alt']
    }
}

SECURE_CROSS_ORIGIN_OPENER_POLICY = 'unsafe-none'
