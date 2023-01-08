
from pathlib import Path
from django.utils import timezone
import os
import sys

from main.constants import PAGES

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-&x$kkv%yo(*nutqe3)=&e@kl9o#ii#vzkwaxg8a=-!fo&cic7n'

DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main.apps.MainConfig',
    'member.apps.MemberConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # System Middleware
    'main.middleware.AllowedClientMiddleware',
    'main.middleware.LoginRequiredMiddleware',
    'main.middleware.AllowedUserMiddleware',
]

ROOT_URLCONF = 'core.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
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
LANGUAGE_CODE = 'ar-ye'
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_TZ = False

# Version
PROJECT_VERSION = '1.0.0'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static/static_collection'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REQUIRED_AUTHENTICATION_PAGES = []

# Logs
LOGS_PATH = BASE_DIR.parent / 'logs'
Path(LOGS_PATH).mkdir(parents=True, exist_ok=True)
LOG_FILE_NAME = str(timezone.datetime.date(timezone.now())) + '_HoneyHome.log'
LOGGING_LEVEL = 'DEBUG' if DEBUG else 'INFO'
HANDLERS = ['console', 'file']
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "{asctime} [{levelname}] - {name}.{module}.('{funcName}') - {message}",
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': sys.__stdout__,
            'formatter': 'simple',
        },
        'file': {
            'level': LOGGING_LEVEL,
            'class': 'logging.FileHandler',
            'filename': LOGS_PATH / LOG_FILE_NAME,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        "django": {
            'handlers': HANDLERS,
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        "django.server": {
            'handlers': HANDLERS,
            'level': os.getenv('DJANGO_LOG_LEVEL', LOGGING_LEVEL),
            'filters': ['require_debug_true'],
            'propagate': False,
        },
        "django.template": {
            'handlers': HANDLERS,
            'level': os.getenv('DJANGO_LOG_LEVEL', LOGGING_LEVEL),
            'filters': ['require_debug_true'],
            'propagate': False,
        },
        "django.db.backends.schema": {
            'handlers': HANDLERS,
            'level': os.getenv('DJANGO_LOG_LEVEL', LOGGING_LEVEL),
            'filters': ['require_debug_true'],
            'propagate': False,
        },
        "django.security.*": {
            'handlers': HANDLERS,
            'level': os.getenv('DJANGO_LOG_LEVEL', LOGGING_LEVEL),
            'filters': ['require_debug_true'],
            'propagate': False,
        },
    },
}

SP = "CSS59XPUZ8"
