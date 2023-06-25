import re
from os import environ

from core.settings.base import *
from core.settings.cron import *
from core.settings.db import *
from core.settings.log import *
from core.settings.mail import *
from core.settings.urls import *

# Version
PROJECT_VERSION = '1.3.1'

# Site Under Maintenance
UNDER_MAINTENANCE = False

# Internationalization
WSGI_APPLICATION = 'core.wsgi.application'

LANGUAGE_CODE = 'ar-ye'

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_TZ = False

DEBUG = False if environ.get('PRODUCTION') == "TRUE" else True

DATA_UPLOAD_MAX_NUMBER_FIELDS = 100

DATA_UPLOAD_MAX_NUMBER_FILES = 5

IGNORABLE_404_URLS = [
    re.compile(r'^/apple-touch-icon.*\.png$'),
    re.compile(r'^/favicon.ico$'),
    re.compile(r'^/robots.txt$'),
    re.compile(r'^/phpmyadmin/'),
    re.compile(r'\.(cgi|php|pl)$'),
]

PRODUCTION = not DEBUG

if PRODUCTION:
    SECURE_SSL_REDIRECT = True

    SECURE_SSL_REDIRECT = True

    SECRET_KEY = environ.get('SECRET_KEY')

    SP = environ.get('ADMIN_PASSWORD')

else:

    SECRET_KEY = 'django-insecure-f82e4206-a63c-11ed-afa1-0242ac120002'

    SP = "CSS59XPUZ8"

# Hosts
ALLOWED_HOSTS = [

]
