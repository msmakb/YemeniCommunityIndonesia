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
    'MEMBER_FORM_POST',
])(
    '0',
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
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
MEDIA_DIR = _NT('str', [
    'PHOTOGRAPHS_DIR',
    'PASSPORTS_DIR',
    'RESIDENCY_IMAGES_DIR',

])(
    'documents/images/photographs',
    'documents/images/passportImages',
    'documents/images/residencyImages',
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
    '0',
    '1'
)
GENDER_AR: Final[tuple[str, ...]] = (
    'ذكر',
    'أنثى'
)
GROUPS = _NT('str', [
    'MANAGER',
    'MEMBER',
])(
    'Manager',
    'Member',
)
ACADEMIC_QUALIFICATION = _NT('str', [
    'PHD',
    'MASTER',
    'BACHELOR',
    'DIPLOMA',
    'SECONDARY',
    'ELEMENTARY',
    'NONE',
])(
    '0',
    '1',
    '2',
    '3',
    '4',
    '5',
    '9',
)
ACADEMIC_QUALIFICATION_AR: Final[tuple[str, ...]] = (
    'دكتوراه',
    'ماجستير',
    'بكالوريوس',
    'دبلوم',
    'ثانوي',
    'أساسي',
    'لايوجد',
)
MEMBERSHIP_TYPE = _NT('str', [
    'STUDENT',
    'INVESTOR',
    'EMPLOYER',
])(
    '0',
    '1',
    '2',
)
MEMBERSHIP_TYPE_AR: Final[tuple[str, ...]] = (
    'طالب',
    'مستثمر',
    'موضف',
)
PERIOD_OF_RESIDENCE = _NT('str', [
    'LEES_THAN_SIX_MONTHS',
    'ONE_YEAR_OR_LESS',
    'YEAR_TO_TWO_YEARS',
    'TWO_YEARS_TO_THREE_YEARS',
    'THREE_YEARS_TO_FOUR_YEARS',
    'FOUR_YEARS_TO_FIVE_YEARS',
    'MORE_THAN_FIVE_YEARS',
])(
    '0',
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
)
PERIOD_OF_RESIDENCE_AR: Final[tuple[str, ...]] = (
    'أقل من 6 شهور',
    'سنة أو أقل',
    'سنة إلى سنتين',
    'سنتين إلى 3 سنوات',
    '3 سنوات إلى 4 سنوات',
    '4 سنوات إلى 5 سنوات',
    'أكثر من 5 سنوات',
)
CHOICES = _NT('tuple', [
    'ACADEMIC_QUALIFICATION',
    'ACCESS_TYPE',
    'ACTION',
    'BLOCK_TYPE',
    'DATA_TYPE',
    'GENDER',
    'MEMBERSHIP_TYPE',
    'PERIOD_OF_RESIDENCE',
])(
    [(aq, ACADEMIC_QUALIFICATION_AR[i])
     for i, aq in enumerate(ACADEMIC_QUALIFICATION)],
    [(access_type, access_type) for access_type in ACCESS_TYPE],
    [(action, action) for action in ACTION],
    [(block_type, block_type) for block_type in BLOCK_TYPES],
    [(data_type, data_type) for data_type in DATA_TYPE],
    [(gender, GENDER_AR[i]) for i, gender in enumerate(GENDER)],
    [(membership_type, MEMBERSHIP_TYPE_AR[i])
     for i, membership_type in enumerate(MEMBERSHIP_TYPE)],
    [(period, PERIOD_OF_RESIDENCE_AR[i])
     for i, period in enumerate(PERIOD_OF_RESIDENCE)]
)
PAGES = _NT('str', [
    'INDEX_PAGE',
    'ABOUT_PAGE',
    'LOGIN_PAGE',
    'LOGOUT',
    'UNAUTHORIZED_PAGE',
    'DASHBOARD',
    'MEMBER_PAGE',
    'MEMBER_FORM_PAGE',
    'DETAIL_MEMBER_PAGE',
])(
    'Index',
    'About',
    'Login',
    'Logout',
    'Unauthorized',
    'Dashboard',
    'Member',
    'MemberFormPage',
    'DetailMemberPage',
)
TEMPLATES = _NT('str', [
    # Main templates
    'INDEX_TEMPLATE',
    'UNAUTHORIZED_TEMPLATE',
    'ABOUT_TEMPLATE',
    'LOGIN_TEMPLATE',
    'DASHBOARD_TEMPLATE',
    'MEMBER_PAGE_TEMPLATE',
    'MEMBER_FORM_TEMPLATE',
    'DETAIL_MEMBER_TEMPLATE',
])(
    # Main templates
    f'{_main_app__templates_folder}/index.html',
    f'{_main_app__templates_folder}/unauthorized.html',
    f'{_main_app__templates_folder}/about.html',
    f'{_main_app__templates_folder}/login.html',
    f'{_main_app__templates_folder}/dashboard.html',
    f'{_main_app__templates_folder}/member_page.html',
    f'{_main_app__templates_folder}/member_form.html',
    f'{_main_app__templates_folder}/detail_member.html',
)
PARAMETERS = _NT('str', [
    "ALLOWED_LOGGED_IN_ATTEMPTS",
    "ALLOWED_LOGGED_IN_ATTEMPTS_RESET",
    "MAX_TEMPORARY_BLOCK",
    "TEMPORARY_BLOCK_PERIOD",
    "TIME_OUT_PERIOD",
    "BETWEEN_POST_REQUESTS_TIME",
    "MAGIC_NUMBER",
    "MEMBERSHIP_EXPIRE_PERIOD",
    "THREE_CHARACTER_PREFIX_FOR_MEMBERSHIP",
    "MEMBER_FORM_POST_LIMIT",
])(
    "ALLOWED_LOGGED_IN_ATTEMPTS",
    "ALLOWED_LOGGED_IN_ATTEMPTS_RESET",
    "MAX_TEMPORARY_BLOCK",
    "TEMPORARY_BLOCK_PERIOD",
    "TIME_OUT_PERIOD",
    "BETWEEN_POST_REQUESTS_TIME",
    "MAGIC_NUMBER",
    "MEMBERSHIP_EXPIRE_PERIOD",
    "THREE_CHARACTER_PREFIX_FOR_MEMBERSHIP",
    "MEMBER_FORM_POST_LIMIT",
)
PERMISSIONS: Final[dict[str, tuple[str, ...]]] = {
    GROUPS.MANAGER: (
        PAGES.DASHBOARD,
        PAGES.DETAIL_MEMBER_PAGE,
    ),
    GROUPS.MEMBER: (
        PAGES.MEMBER_PAGE,
    )
}
RESTRICTED_PAGES: Final[list[str]] = [
    page for pages in PERMISSIONS.values() for page in pages
]
