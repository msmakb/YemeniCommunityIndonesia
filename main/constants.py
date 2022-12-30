from collections import namedtuple as _NT
from typing import Final

# ------------------------------------ private ------------------------------------ #
_main_app__templates_folder: Final[str] = '.'

# ---------------------------------- public --------------------------------------- #
PERSONAL_PHOTOS_FOLDER: Final[str] = 'photographs'
GET_METHOD: Final[str] = 'GET'
POST_METHOD: Final[str] = 'POST'
DELETE_METHOD: Final[str] = 'DELETE'
ROWS_PER_PAGE: Final[int] = 10
ADMIN_SITE = _NT('str', [
    'SITE_HEADER',
    'SITE_TITLE',
    'INDEX_TITLE',
])(
    'إدارة الجالية اليمنية في إندونيسيا',
    'الجالية اليمنية في إندونيسيا',
    'لوحة تحكم المسؤول',
)
LOGGERS = _NT('str', [
    'MAIN',
])(
    'HoneyHome.Main',
)
PAGES = _NT('str', [
    'INDEX_PAGE'
    ]
)(
    'Index'
)
TEMPLATES = _NT('str', [
    # Main templates
    'INDEX_TEMPLATE',
    ]
)(
    # Main templates
    f'{_main_app__templates_folder}/index.html',
)