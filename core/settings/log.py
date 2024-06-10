from os import environ
import sys
from pathlib import Path
from logging import Filter

from django.core.exceptions import DisallowedHost
from django.utils import timezone

from main.constants import _base_dir, LOGGERS


DEFAULT_EXCLUDE_EXCEPTIONS = [
    DisallowedHost,
]


class ExceptionFilter(Filter):
    def __init__(self, exclude_exceptions=DEFAULT_EXCLUDE_EXCEPTIONS, **kwargs):
        super().__init__(**kwargs)
        self.EXCLUDE_EXCEPTIONS = exclude_exceptions

    def filter(self, record):
        if record.exc_info:
            exception_type, *_ = record.exc_info
            for excluded_exception in self.EXCLUDE_EXCEPTIONS:
                if issubclass(exception_type, excluded_exception):
                    return False
        return True


LOGGING_LEVEL = 'INFO' if environ.get('PRODUCTION') == 'TRUE' else 'DEBUG'

LOGS_PATH = _base_dir.parent / 'logs'

Path(LOGS_PATH).mkdir(parents=True, exist_ok=True)

LOG_FILE_NAME = str(timezone.datetime.date(timezone.now())) + '_YCI.log'

if environ.get('PRODUCTION') == "TRUE":
    HANDLERS = [
        'file',
        'mail_admins',
    ]
else:
    HANDLERS = [
        'file',
        'console',
    ]

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
        'exception_filter': {
            '()': ExceptionFilter,
        },
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
            'encoding': 'utf-8',
            'filters': [
                'exception_filter',
            ],
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
            'include_html': True,
            'filters': [
                'exception_filter',
            ],
        }
    },
    'loggers': {
        "django": {
            'handlers': HANDLERS,
            'level': LOGGING_LEVEL,
            'propagate': False,
        },
        "django.server": {
            'handlers': HANDLERS,
            'level': LOGGING_LEVEL,
            'propagate': False,
        },
        "django.template": {
            'handlers': HANDLERS,
            'level': LOGGING_LEVEL,
            'propagate': False,
        },
        "django.db.backends.schema": {
            'handlers': HANDLERS,
            'level': LOGGING_LEVEL,
            'propagate': False,
        },
        "django.security.*": {
            'handlers': HANDLERS,
            'level': LOGGING_LEVEL,
            'propagate': False,
        },
        LOGGERS.MIDDLEWARE: {
            'handlers': HANDLERS,
            'level': 'WARNING',
            'propagate': False,
        },
        LOGGERS.MAIN: {
            'handlers': HANDLERS,
            'level': LOGGING_LEVEL,
            'propagate': False,
        },
        LOGGERS.MODELS: {
            'handlers': HANDLERS,
            'level': LOGGING_LEVEL,
            'propagate': False,
        },
        LOGGERS.BROADCAST: {
            'handlers': HANDLERS,
            'level': LOGGING_LEVEL,
            'propagate': False,
        },
        LOGGERS.PARAMETER: {
            'handlers': HANDLERS,
            'level': LOGGING_LEVEL,
            'propagate': False,
        },
        LOGGERS.FORMS: {
            'handlers': HANDLERS,
            'level': LOGGING_LEVEL,
            'propagate': False,
        },
        "google": {
            'handlers': HANDLERS,
            'level': LOGGING_LEVEL,
            'propagate': False,
        },
    },
}
