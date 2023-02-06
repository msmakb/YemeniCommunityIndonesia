from os import environ

from core.settings.base import *
from core.settings.cron import *
from core.settings.db import *
from core.settings.log import *
from core.settings.mail import *
from core.settings.urls import *

# Version
PROJECT_VERSION = '1.0.0'

# Internationalization
WSGI_APPLICATION = 'core.wsgi.application'

LANGUAGE_CODE = 'ar-ye'

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_TZ = False

DEBUG = False if environ.get('PRODUCTION') == "TRUE" else True

PRODUCTION = not DEBUG

if PRODUCTION:
    SECRET_KEY = environ.get('SECRET_KEY')
    SP = environ.get('ADMIN_PASSWORD')
else:
    SECRET_KEY = 'django-insecure-f82e4206-a63c-11ed-afa1-0242ac120002'
    SP = "CSS59XPUZ8"
