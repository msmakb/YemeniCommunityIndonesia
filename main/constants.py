from typing import Final

# ------------------------------------ private ------------------------------------ #
from collections import namedtuple as _NT
_main_app__templates_folder: Final[str] = '.'

# ---------------------------------- public --------------------------------------- #
BASE_MODEL_FIELDS: Final[tuple[str, ...]] = ('created', 'updated')
HTML_TAGS_PATTERN: Final[str] = '<.*?>((.|\n)*)<\/.*?>'
GET_METHOD: Final[str] = 'GET'
POST_METHOD: Final[str] = 'POST'
DELETE_METHOD: Final[str] = 'DELETE'
ROWS_PER_PAGE: Final[int] = 10
ACCESS_TYPE = _NT('str', [
    'No_ACCESS',
    'ADMIN_ACCESS',
    'FULL_ACCESS'
])(
    '0',
    '1',
    '2'
)
ACTION = _NT('str', [
    'FIRST_VISIT',
    'LOGGED_IN',
    'LOGGED_OUT',
    'LOGGED_FAILED',
    'NORMAL_POST',
    'SUSPICIOUS_POST',
    'ATTACK_ATTEMPT',
])(
    '0',
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
)
BLOCK_TYPES = _NT('str', [
    'UNBLOCKED',
    'TEMPORARY',
    'INDEFINITELY',
])(
    '0',
    '1',
    '2',
)
DATA_TYPE = _NT('str', [
    'STRING',
    'INTEGER',
    'FLOAT',
    'BOOLEAN'
])(
    '0',
    '1',
    '2',
    '3'
)
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
    'MIDDLEWARE',
    'MODELS',
])(
    'HoneyHome.Main',
    'HoneyHome.Middleware',
    'HoneyHome.Models',
)
GENDER = _NT('str', [
    'MALE',
    'FEMALE'
])(
    'Male',
    'Female'
)
GROUPS = _NT('str', [
    'ADMIN',
    'MEMBER',
])(
    'Admin',
    'Member',
)
CHOICES = _NT('tuple', [
    'ACCESS_TYPE',
    'ACTION',
    'BLOCK_TYPE',
    'DATA_TYPE',
    'GENDER',
])(
    [(access_type, access_type) for access_type in ACCESS_TYPE],
    [(action, action) for action in ACTION],
    [(block_type, block_type) for block_type in BLOCK_TYPES],
    [(data_type, data_type) for data_type in DATA_TYPE],
    [(gender, gender) for gender in GENDER],
)
PAGES = _NT('str', [
    'INDEX_PAGE',
    'ABOUT_PAGE',
    'LOGOUT',
    'UNAUTHORIZED_PAGE',
])(
    'Index',
    'About',
    'Logout',
    'Unauthorized'
)
TEMPLATES = _NT('str', [
    # Main templates
    'INDEX_TEMPLATE',
    'UNAUTHORIZED_TEMPLATE',
    'ABOUT_TEMPLATE',
])(
    # Main templates
    f'{_main_app__templates_folder}/index.html',
    f'{_main_app__templates_folder}/unauthorized.html',
    f'{_main_app__templates_folder}/about.html',
)
PARAMETERS = _NT('str', [
    "ALLOWED_LOGGED_IN_ATTEMPTS",
    "ALLOWED_LOGGED_IN_ATTEMPTS_RESET",
    "MAX_TEMPORARY_BLOCK",
    "TEMPORARY_BLOCK_PERIOD",
    "TIME_OUT_PERIOD",
    "BETWEEN_POST_REQUESTS_TIME",
    "MAGIC_NUMBER",
])(
    "ALLOWED_LOGGED_IN_ATTEMPTS",
    "ALLOWED_LOGGED_IN_ATTEMPTS_RESET",
    "MAX_TEMPORARY_BLOCK",
    "TEMPORARY_BLOCK_PERIOD",
    "TIME_OUT_PERIOD",
    "BETWEEN_POST_REQUESTS_TIME",
    "MAGIC_NUMBER",
)
