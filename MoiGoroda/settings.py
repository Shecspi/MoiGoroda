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

import sentry_sdk
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
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
    'markdownify',
    'dashboard',
    'share.apps.ShareConfig',
    'subscribe',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Debug toolbar находится в DEV-зависимостях, поэтому на продакшене он не устанавливается.
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

ROOT_URLCONF = 'MoiGoroda.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'MoiGoroda.context_processors.general_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'MoiGoroda.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE'),
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT'),
    }
}

if 'test' in sys.argv:
    DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'mydatabase'}

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

TIME_ZONE = os.getenv('TIME_ZONE')

USE_I18N = True

USE_TZ = os.getenv('USE_TZ') == 'True'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.getenv('STATIC_ROOT')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

LOGIN_REDIRECT_URL = '/city/all/list'
LOGOUT_REDIRECT_URL = '/'

INTERNAL_IPS = ['127.0.0.1', '0.0.0.0']

LOGIN_URL = '/account/signin'

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS') == 'True'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL') == 'True'

SERVER_EMAIL = os.getenv('SERVER_EMAIL')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
ADMINS = [
    (os.getenv('ADMIN_NAME'), os.getenv('ADMIN_EMAIL')),
]

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
        'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'},
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'detail_app': {
            'format': '%(levelname)-8s %(asctime)-22s %(IP)-18s %(user)-10s %(message)-s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'detail_django': {
            'format': '%(levelname)-8s %(asctime)-22s INTERNAL           DJANGO     %(message)-s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {'format': '%(levelname)-8s %(message)s'},
    },
    'handlers': {
        # Запись в файл логов приложения
        # Только при DEBUG=False
        'to_file_app': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'detail_app',
            'filename': LOG_FIlE_PATH,
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
        },
        # Запись в файл логов Django
        # Только при DEBUG=False
        'to_file_django': {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'logging.FileHandler',
            'formatter': 'detail_django',
            'filename': LOG_FIlE_PATH,
        },
        # Отправка писем с ошибками на почту
        # Только при DEBUG=False
        'to_email_general': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        # Отправка регистрационного письма на почту
        # Только при DEBUG=False
        'to_email_signup': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        # Вывод в консоль логов приложения
        # только при DEBUG=True
        'to_console_app': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'detail_app',
        },
        # Вывод в консоль логов Django
        # только при DEBUG=True
        'to_console_django': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'detail_django',
        },
    },
    'loggers': {
        # Базовый логгер. Используется для логирования действий внутри приложения
        'base': {
            'level': 'INFO',
            'propogate': True,
            'handlers': ['to_console_app', 'to_file_app', 'to_email_general'],
        },
        # Логгер, который срабатывает при регистрации пользователей
        'account.views': {
            'level': 'INFO',
            'propogate': True,
            'handlers': ['to_file_app', 'to_email_signup'],
        },
        # Логгер для перехватывания логирования Django
        'django': {
            'level': 'INFO',
            'propogate': True,
            'handlers': ['to_console_django', 'to_file_django'],
        },
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# MDEditor
X_FRAME_OPTIONS = 'SAMEORIGIN'
MDEDITOR_CONFIGS = {'default': {'language': 'en'}}

# Markdownify
MARKDOWNIFY = {
    'default': {
        'WHITELIST_TAGS': [
            # Протестированные теги
            'a',
            'blockquote',
            'code',
            'img',
            'em',
            'h1',
            'h2',
            'h3',
            'h4',
            'h5',
            'h6',
            'strong',
            # Непротестированные теги
            'li',
            'ol',
            'p',
            'ul',
        ],
        'WHITELIST_ATTRS': ['href', 'src', 'alt'],
    }
}

SECURE_CROSS_ORIGIN_OPENER_POLICY = 'unsafe-none'

################
# -- Sentry -- #
################
if not DEBUG:
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_TOKEN'),
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE')),
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=float(os.getenv('SENTRY_PROFILES_SAMPLE_RATE')),
    )
