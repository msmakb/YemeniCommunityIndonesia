from pathlib import Path
from os import environ

from main.constants import _base_dir

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': _base_dir / 'db.sqlite3',
        # 'ENGINE': 'django.db.backends.mysql',
        # 'NAME': environ.get(DB_NAME),
        # 'USER': environ.get(DB_USER),
        # 'PASSWORD': environ.get(DB_PASSWORD),
        # 'HOST':'localhost',
        # 'PORT':'3306',
    }
}

# Database Backup
BACKUP_FOLDER = _base_dir.parent / 'backup'

Path(BACKUP_FOLDER).mkdir(parents=True, exist_ok=True)

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'

DBBACKUP_STORAGE_OPTIONS = {'location': BACKUP_FOLDER}

# Caches
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

SESSION_CACHE_ALIAS = 'default'
