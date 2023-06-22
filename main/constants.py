from collections import namedtuple as _NT
from pathlib import Path
import json
from typing import Final

# ------------------------------------ private ------------------------------------ #
_main_app__templates_folder: Final[str] = '.'
_email__templates_folder: Final[str] = _main_app__templates_folder + '/email'
_base_dir = Path(__file__).resolve().parent.parent
with open(_base_dir / "data/cities.json", "r", encoding="utf-8") as _file:
    _cities: dict[str, str] = json.load(_file)
with open(_base_dir / "data/country_code.json", "r", encoding="utf-8") as _file:
    _country_codes: dict[str, str] = json.load(_file)
# ---------------------------------- public --------------------------------------- #
PHONE_NUMBERS_COUNTRY_CODES: Final[dict[str, str]] = _country_codes
CITIES: Final[dict[str, str]] = dict(sorted(_cities.items()))
BASE_MODEL_FIELDS: Final[tuple[str, ...]] = ('created', 'updated')
HTML_TAGS_PATTERN: Final[str] = '<.*?>((.|\n)*)<\/.*?>'
GET_METHOD: Final[str] = 'GET'
POST_METHOD: Final[str] = 'POST'
DELETE_METHOD: Final[str] = 'DELETE'
ROWS_PER_PAGE: Final[int] = 10
DEFAULT_CACHE_EXPIRE: Final[int] = 86_400  # One day
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
    'EMPTY_1',
    'EMPTY_2',
    'DELETE_USER',
    'ADD_ROLE',
    'UPDATE_ROLE',
    'DELETE_ROLE',
    'ADD_USER',
    'COMPLETE_USER_REGISTRATION',
    'UPDATE_USER',
    'BROADCAST',
    'ACCEPT_MEMBER',
    'DENY_MEMBER',
    'SETTINGS_CHANGE',
    'DONATION',
    'VALIDATE_DONATION',
    'ADD_MEMBERSHIP_PAYMENT',
    'CHECK_PAYMENT',
])(
    '0',
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9',
    '10',
    '11',
    '12',
    '13',
    '14',
    '15',
    '16',
    '17',
    '18',
    '19',
    '20',
    '21',
    '22',
    '23',
    '24',
)
ACTION_STR: tuple[str, ...] = (
    'FIRST_VISIT',
    'LOGGED_IN',
    'LOGGED_OUT',
    'LOGGED_FAILED',
    'NORMAL_POST',
    'SUSPICIOUS_POST',
    'ATTACK_ATTEMPT',
    'MEMBER_FORM_POST',
    'EMPTY_1',
    'EMPTY_2',
    'DELETE_USER',
    'ADD_ROLE',
    'UPDATE_ROLE',
    'DELETE_ROLE',
    'ADD_USER',
    'COMPLETE_USER_REGISTRATION',
    'UPDATE_USER',
    'BROADCAST',
    'ACCEPT_MEMBER',
    'DENY_MEMBER',
    'SETTINGS_CHANGE',
    'DONATION',
    'VALIDATE_DONATION',
    'ADD_MEMBERSHIP_PAYMENT',
    'CHECK_PAYMENT',
)
ACTION_STR_AR: tuple[str, ...] = (
    'زيارة أولى',
    'تسجيل دخول',
    'تسجيل خروج',
    'تسجيل دخول فاشل',
    'NORMAL_POST',
    'محاولة مشتبهة',
    'محاولة مشتبهة',
    'تقديم نموذج',
    'EMPTY_1',
    'EMPTY_2',
    'حذف مستخدم',
    'إضافة وظيفة جديدة',
    'تعديل وظيفة',
    'حذف وظيفة',
    'إضافة مستخدم جديدة',
    'استكمال تسجيل مستخدم',
    'تعديل بيانات مستخدم',
    'برودكاست',
    'قبول سجل',
    'رفض سجل',
    'تغير إعدادات',
    'تبرع',
    'تحقق من تبرع',
    'دفع اشتراك',
    'تحقق دفع اشتراك',
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
BLOCK_TYPES_AR: Final[tuple[str, ...]] = (
    'ملغى حظره',
    'حظر مؤقت',
    'حظر مؤبد',
)
DATA_TYPE = _NT('str', [
    'STRING',
    'INTEGER',
    'FLOAT',
    'BOOLEAN',
    'EMAIL',
    'IMAGE_FILE',
])(
    '0',
    '1',
    '2',
    '3',
    '4',
    '5',
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
    'MEMBERSHIP_IMAGES_DIR',
    'MEMBERSHIP_PAYMENT_RECEIPTS_DIR',
    'DONATIONS_RECEIPTS_DIR',
    'EMAIL_ATTACHMENTS_DIR',
    'PUBLIC_DIR',

])(
    'documents/images/photographs',
    'documents/images/passportImages',
    'documents/images/residencyImages',
    'documents/images/membershipImages',
    'documents/images/membershipReceipts',
    'documents/images/donationsReceipts',
    'broadcast/emailAttachment',
    'public/',
)
_MIME_TYPE: dict[str, str] = {
    'AVI': 'video/x-msvideo',
    'JPEG': 'image/jpeg',
    'MP4': 'video/mp4',
    'MP3': 'audio/mpeg',
    'PNG': 'image/png',
    'PDF': 'application/pdf',
    'RAR': 'application/vnd.rar',
    'TEXT': 'text/plain',
    'WAV': 'audio/wav',
    'MS_EXCEL': 'application/vnd.ms-excel',
    'MS_POWERPOINT': 'application/vnd.ms-powerpoint',
    'MS_EXCEL_OPEN_XML': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'MS_POWERPOINT_OPEN_XML': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
}
MIME_TYPE = _NT('str', [
    'AVI',  # .avi	AVI: Audio Video Interleave
    'JPEG',  # .jpeg, .jpg	JPEG images
    'MP4',  # .mp4	MP4 video
    'MP3',  # .mp3	MP3 audio
    'PNG',  # .png	Portable Network Graphics
    'PDF',  # .pdf	Adobe Portable Document Format (PDF)
    'RAR',  # .rar	RAR archive
    'TEXT',  # .txt	Text, (generally ASCII or ISO 8859-n)
    'WAV',  # .wav	Waveform Audio Format
    'MS_EXCEL',  # .xls	Microsoft Excel
    'MS_POWERPOINT',  # .ppt	Microsoft PowerPoint
    'MS_EXCEL_OPEN_XML',  # .xlsx	Microsoft Excel (OpenXML)
    'MS_POWERPOINT_OPEN_XML',  # .pptx	Microsoft PowerPoint (OpenXML)
])(
    _MIME_TYPE.get('AVI'),
    _MIME_TYPE.get('JPEG'),
    _MIME_TYPE.get('MP4'),
    _MIME_TYPE.get('MP3'),
    _MIME_TYPE.get('PNG'),
    _MIME_TYPE.get('PDF'),
    _MIME_TYPE.get('RAR'),
    _MIME_TYPE.get('TEXT'),
    _MIME_TYPE.get('WAV'),
    _MIME_TYPE.get('MS_EXCEL'),
    _MIME_TYPE.get('MS_POWERPOINT'),
    _MIME_TYPE.get('MS_EXCEL_OPEN_XML'),
    _MIME_TYPE.get('MS_POWERPOINT_OPEN_XML'),
)
LOGGERS = _NT('str', [
    'MAIN',
    'MIDDLEWARE',
    'MODELS',
    'BROADCAST',
    'PARAMETER',
])(
    'YCI.Main',
    'YCI.Middleware',
    'YCI.Models',
    'YCI.Broadcast',
    'YCI.Parameter',
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
    'MEMBERS',
    'BROADCAST',
    'MONITOR',
    'PARAMETER',
    'COMPANY_USER',
    'PAYMENT',
    'DONATION',
])(
    'Members',
    'Broadcast',
    'Monitor',
    'Parameter',
    'Company User',
    'Payment',
    'Donation',
)
GROUPS_AR: Final[dict[str, str]] = {
    GROUPS.MEMBERS: 'الأعضاء',
    GROUPS.BROADCAST: 'برودكاست',
    GROUPS.MONITOR: 'مراقبة',
    GROUPS.PARAMETER: 'اعدادات النظام',
    GROUPS.COMPANY_USER: 'إدارة المستخدم',
    GROUPS.PAYMENT: 'مدفوعات العضوية',
    GROUPS.DONATION: 'التبرعات',
}
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
    '6',
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
JOB_TITLE = _NT('str', [
    'STUDENT',
    'EMPLOYER',
    'INVESTOR',
    'OTHER',
    'NONE'
])(
    '0',
    '1',
    '2',
    '3',
    '4'
)
JOB_TITLE_AR: Final[tuple[str, ...]] = (
    'طالب',
    'موظف',
    'مستثمر أو رجل أعمال',
    'غير ذلك',
    'لا يوجد'
)
MEMBERSHIP_TYPE = _NT('str', [
    'STUDENT',
    'INVESTOR',
    'EMPLOYER',
    'GENERAL',
])(
    '0',
    '1',
    '2',
    '3',
)
MEMBERSHIP_TYPE_EN: Final[tuple[str, ...]] = (
    'STUDENT',
    'INVESTOR',
    'EMPLOYEE',
    'GENERAL',
)
MEMBERSHIP_TYPE_AR: Final[tuple[str, ...]] = (
    'طالب',
    'مستثمر',
    'موظف',
    'عامة',
)
MONTHS_AR = [
    'يناير',
    'فبراير',
    'مارس',
    'أبريل',
    'مايو',
    'يونيو',
    'يوليو',
    'أغسطس',
    'سبتمبر',
    'أكتوبر',
    'نوفمبر',
    'ديسمبر',
]
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
PAYMENT_STATUS = _NT('str', [
    'PENDING',
    'APPROVED',
    'REJECTED',
])(
    '0',
    '1',
    '2',
)
PAYMENT_STATUS_AR: Final[tuple[str, ...]] = (
    'قيد المعالجة',
    'معتمد',
    'مرفوض',
)
CHOICES = _NT('tuple', [
    'ACADEMIC_QUALIFICATION',
    'ACCESS_TYPE',
    'ACTION',
    'BLOCK_TYPE',
    'CITIES',
    'DATA_TYPE',
    'GENDER',
    'JOB_TITLE',
    'MEMBERSHIP_TYPE',
    'MIME_TYPE',
    'PERIOD_OF_RESIDENCE',
    'PAYMENT_STATUS',
])(
    [(aq, ACADEMIC_QUALIFICATION_AR[i])
     for i, aq in enumerate(ACADEMIC_QUALIFICATION)],
    [(access_type, access_type) for access_type in ACCESS_TYPE],
    [(action, action) for action in ACTION],
    [(block_type, block_type) for block_type in BLOCK_TYPES],
    [(k, k) for k in CITIES.keys()],
    [(data_type, data_type) for data_type in DATA_TYPE],
    [(gender, GENDER_AR[i]) for i, gender in enumerate(GENDER)],
    [(job_title, JOB_TITLE_AR[i]) for i, job_title in enumerate(JOB_TITLE)],
    [(membership_type, MEMBERSHIP_TYPE_AR[i])
     for i, membership_type in enumerate(MEMBERSHIP_TYPE)],
    [(value, key) for key, value in _MIME_TYPE.items()],
    [(period, PERIOD_OF_RESIDENCE_AR[i])
     for i, period in enumerate(PERIOD_OF_RESIDENCE)],
    [(status, PAYMENT_STATUS_AR[i])
     for i, status in enumerate(PAYMENT_STATUS)],
)
PAGES = _NT('str', [
    # Main pages
    'INDEX_PAGE',
    'MEMBERSHIP_TERMS_PAGE',
    'ABOUT_PAGE',
    'LOGIN_PAGE',
    'LOGOUT',
    'UNAUTHORIZED_PAGE',
    'DONATION_PAGE',
    'THANKS_FOR_DONATION_PAGE',
    'DONATION_LIST_PAGE',

    # Member pages
    'STAFF_DASHBOARD',
    'MEMBERS_PAGE',
    'MEMBER_DASHBOARD',
    'DOWNLOAD_MEMBERSHIP_PAGE',
    'MEMBER_FORM_PAGE',
    'DETAIL_MEMBER_PAGE',
    'THANK_YOU_PAGE',
    'MEMBERSHIP_CARD_PAGE',

    # Broadcast pages
    'BROADCAST_PAGE',
    'DETAIL_BROADCAST_PAGE',
    'ADD_BROADCAST_PAGE',
    'UPDATE_BROADCAST_PAGE',
    'ADD_ATTACHMENT_PAGE',
    'DELETE_ATTACHMENT_PAGE',
    'UPDATE_ATTACH_MEMBERSHIP_CARD_API',

    # Parameters pages
    'SETTINGS_PAGE',

    # Monitor pages
    'MONITOR_PAGE',
    'ACTIVITY_LOG_PAGE',
    'BLOCK_LIST_PAGE',

    # Company user pages
    'COMPANY_USERS_PAGE',
    'ADD_COMPANY_USER_PAGE',
    'UPDATE_COMPANY_USER_PAGE',
    'DELETE_COMPANY_USER_PAGE',
    'ROLES_PAGE',
    'ADD_ROLE_PAGE',
    'UPDATE_ROLE_PAGE',
    'DELETE_ROLE_PAGE',
    'COMPANY_USER_REGISTRATION_PAGE',

    # Payment pages
    'MEMBERSHIP_PAYMENT_PAGE',
    'MEMBERSHIP_PAYMENT_HISTORY_PAGE',
    'MEMBERSHIP_PAYMENT_RECEIPT',
    'MEMBERSHIP_PAYMENT_LIST_PAGE',
    'MEMBERSHIP_PAYMENT_PENDING_LIST_PAGE',
    'GET_PAYMENT_PERIOD_API',
])(
    # Main pages
    'Index',
    'MembershipTerms',
    'About',
    'Login',
    'Logout',
    'Unauthorized',
    'Donation',
    'ThanksForDonation',
    'DonationListPage',

    # Member pages
    'StaffDashboard',
    'MembersPage',
    'MemberDashboard',
    'Download-Membership',
    'MemberFormPage',
    'DetailMemberPage',
    'ThankYouPage',
    'MembershipCardPage',

    # Broadcast pages
    'BroadcastPage',
    'DetailBroadcastPage',
    'AddBroadcastPage',
    'UpdateBroadcastPage',
    'AddAttachmentPage',
    'DeleteAttachmentPage',
    'UpdateAttachMembershipCardApi',

    # Parameter pages
    'SettingsPage',

    # Monitor pages
    'MonitorPage',
    'ActivityLogPage',
    'BlockListPage',

    # Company user pages
    'CompanyUsersPage',
    'AddCompanyUserPage',
    'UpdateCompanyUserPage',
    'DeleteCompanyUserPage',
    'RolesPage',
    'AddRolePage',
    'UpdateRolePage',
    'DeleteRolePage',
    'CompanyUserRegistrationPage',

    # Payment pages
    'MembershipPaymentPage',
    'MembershipPaymentHistoryPage',
    'MembershipPaymentReceipt',
    'MembershipPaymentListPage',
    'MembershipPaymentPendingListPage',
    'GetPaymentPeriodApi',
)
TEMPLATES = _NT('str', [
    # Main templates
    'UNDER_MAINTENANCE_PAGE_TEMPLATE',
    'INDEX_TEMPLATE',
    'UNAUTHORIZED_TEMPLATE',
    'MEMBERSHIP_TERMS_TEMPLATE',
    'ABOUT_TEMPLATE',
    'LOGIN_TEMPLATE',
    'DONATION_TEMPLATE',
    'THANKS_FOR_DONATION_TEMPLATE',
    'DONATION_LIST_PAGE_TEMPLATE',

    # Member templates
    'DASHBOARD_TEMPLATE',
    'MEMBERS_PAGE_TEMPLATE',
    'MEMBER_PAGE_TEMPLATE',
    'MEMBER_FORM_TEMPLATE',
    'DETAIL_MEMBER_TEMPLATE',
    'THANK_YOU_TEMPLATE',
    'MEMBERSHIP_CARD_PAGE_TEMPLATE',

    # Broadcast Template
    'BROADCAST_PAGE_TEMPLATE',
    'DETAIL_BROADCAST_PAGE_TEMPLATE',
    'ADD_UPDATE_BROADCAST_PAGE_TEMPLATE',
    'ADD_ATTACHMENT_PAGE_TEMPLATE',

    # Parameter template
    'SYSTEM_SETTINGS_PAGE_TEMPLATE',

    # Monitor templates
    'MONITOR_PAGE_TEMPLATE',
    'ACTIVITY_LOG_PAGE_TEMPLATE',
    'BLOCK_LIST_PAGE_TEMPLATE',

    # Company user templates
    'COMPANY_USERS_PAGE_TEMPLATE',
    'ADD_UPDATE_COMPANY_USER_PAGE_TEMPLATE',
    'ROLES_PAGE_TEMPLATE',
    'ADD_UPDATE_ROLE_PAGE_TEMPLATE',
    'COMPANY_USER_REGISTRATION_PAGE_TEMPLATE',

    # Payment templates
    'MEMBERSHIP_PAYMENT_PAGE_TEMPLATE',
    'MEMBERSHIP_PAYMENT_HISTORY_PAGE_TEMPLATE',
    'MEMBERSHIP_PAYMENT_LIST_PAGE_TEMPLATE',
    'MEMBERSHIP_PAYMENT_PENDING_LIST_PAGE_TEMPLATE',

    # Email template
    'THANK_YOU_EMAIL_TEMPLATE',
    'APPROVE_MEMBER_EMAIL_TEMPLATE',
    'EMAIL_FOOTER_TEMPLATE',
    'NEW_COMPANY_USER_EMAIL_TEMPLATE',
    'MEMBERSHIP_PAYMENT_EMAIL_TEMPLATE',
    'MEMBERSHIP_PAYMENT_APPROVED_EMAIL_TEMPLATE',
    'MEMBERSHIP_PAYMENT_REJECTED_EMAIL_TEMPLATE',
])(
    # Main templates
    f'{_main_app__templates_folder}/under_maintenance.html',
    f'{_main_app__templates_folder}/index.html',
    f'{_main_app__templates_folder}/unauthorized.html',
    f'{_main_app__templates_folder}/membership_terms.html',
    f'{_main_app__templates_folder}/about.html',
    f'{_main_app__templates_folder}/login.html',
    f'{_main_app__templates_folder}/donation.html',
    f'{_main_app__templates_folder}/thanks_for_donation.html',
    f'{_main_app__templates_folder}/donation_list.html',

    # Member templates
    f'{_main_app__templates_folder}/dashboard.html',
    f'{_main_app__templates_folder}/members_page.html',
    f'{_main_app__templates_folder}/member_page.html',
    f'{_main_app__templates_folder}/member_form.html',
    f'{_main_app__templates_folder}/detail_member.html',
    f'{_main_app__templates_folder}/thank_you.html',
    f'{_main_app__templates_folder}/membership_card.html',

    # Broadcast templates
    f'{_main_app__templates_folder}/broadcasts.html',
    f'{_main_app__templates_folder}/detail_broadcast.html',
    f'{_main_app__templates_folder}/add_update_broadcast.html',
    f'{_main_app__templates_folder}/add_attachment.html',

    # Parameter templates
    f'{_main_app__templates_folder}/system_settings.html',

    # Monitor templates
    f'{_main_app__templates_folder}/monitor.html',
    f'{_main_app__templates_folder}/activity_log.html',
    f'{_main_app__templates_folder}/block_list.html',

    # Company user templates
    f'{_main_app__templates_folder}/company_users.html',
    f'{_main_app__templates_folder}/add_update_company_user.html',
    f'{_main_app__templates_folder}/roles.html',
    f'{_main_app__templates_folder}/add_update_role.html',
    f'{_main_app__templates_folder}/company_user_registration_page.html',

    # Payment templates
    f'{_main_app__templates_folder}/membership_payment.html',
    f'{_main_app__templates_folder}/membership_payment_history.html',
    f'{_main_app__templates_folder}/membership_payment_list.html',
    f'{_main_app__templates_folder}/membership_payment_pending_list.html',

    # Email templates
    f'{_email__templates_folder}/thank_you_email.html',
    f'{_email__templates_folder}/approve_member_email.html',
    f'{_email__templates_folder}/email_footer.html',
    f'{_email__templates_folder}/new_company_user_email.html',
    f'{_email__templates_folder}/membership_payment_email.html',
    f'{_email__templates_folder}/membership_payment_approved_email.html',
    f'{_email__templates_folder}/membership_payment_rejected_email.html',
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
    "IMAGE_MAX_SIZE",
    "REMOVE_BG_API_KEY",
    "PLACEHOLDER_EMAIL",
    "OPEN_MEMBER_REGISTRATION_FORM",
    "MEMBERSHIP_TRANSFER_INFO_IMAGE",
    "REQUEST_MAX_LIMIT_PER_SECOND",
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
    "IMAGE_MAX_SIZE",
    "REMOVE_BG_API_KEY",
    "PLACEHOLDER_EMAIL",
    "OPEN_MEMBER_REGISTRATION_FORM",
    "MEMBERSHIP_TRANSFER_INFO_IMAGE",
    "REQUEST_MAX_LIMIT_PER_SECOND",
)
CACHE = _NT('str', [
    "LAST_AUDIT_ENTRY_QUERYSET",
    "ALLOWED_ClIENTS",
])(
    "LAST_AUDIT_ENTRY_QUERYSET",
    "ALLOWED_ClIENTS",
)
STAFF_PERMISSIONS: Final[dict[str, tuple[str, ...]]] = {
    "COMMON": (
        PAGES.STAFF_DASHBOARD,
    ),
    GROUPS.MEMBERS: (
        PAGES.MEMBERS_PAGE,
        PAGES.DETAIL_MEMBER_PAGE,
    ),
    GROUPS.BROADCAST: (
        PAGES.BROADCAST_PAGE,
        PAGES.DETAIL_BROADCAST_PAGE,
        PAGES.ADD_BROADCAST_PAGE,
        PAGES.UPDATE_BROADCAST_PAGE,
        PAGES.ADD_ATTACHMENT_PAGE,
        PAGES.DELETE_ATTACHMENT_PAGE,
        PAGES.UPDATE_ATTACH_MEMBERSHIP_CARD_API,
    ),
    GROUPS.PARAMETER: (
        PAGES.SETTINGS_PAGE,
    ),
    GROUPS.MONITOR: (
        PAGES.MONITOR_PAGE,
        PAGES.ACTIVITY_LOG_PAGE,
        PAGES.BLOCK_LIST_PAGE,
    ),
    GROUPS.COMPANY_USER: (
        PAGES.COMPANY_USERS_PAGE,
        PAGES.ADD_COMPANY_USER_PAGE,
        PAGES.UPDATE_COMPANY_USER_PAGE,
        PAGES.DELETE_COMPANY_USER_PAGE,
        PAGES.ROLES_PAGE,
        PAGES.ADD_ROLE_PAGE,
        PAGES.UPDATE_ROLE_PAGE,
        PAGES.DELETE_ROLE_PAGE,
    ),
    GROUPS.PAYMENT: (
        PAGES.MEMBERSHIP_PAYMENT_LIST_PAGE,
        PAGES.MEMBERSHIP_PAYMENT_PENDING_LIST_PAGE,
        PAGES.GET_PAYMENT_PERIOD_API,
    ),
    GROUPS.DONATION: (
        PAGES.DONATION_LIST_PAGE,
    ),
}
NON_STAFF_PERMISSIONS: Final[dict[str, tuple[str, ...]]] = {
    "COMMON": (
        PAGES.MEMBER_DASHBOARD,
    ),
    'WITH_MEMBERSHIP_ONLY': {
        PAGES.MEMBERSHIP_CARD_PAGE,
        PAGES.MEMBERSHIP_PAYMENT_PAGE,
        PAGES.MEMBERSHIP_PAYMENT_RECEIPT,
        PAGES.MEMBERSHIP_PAYMENT_HISTORY_PAGE,
        PAGES.GET_PAYMENT_PERIOD_API,
    }
}
STAFF_RESTRICTED_PAGES: Final[list[str]] = [
    page for pages in STAFF_PERMISSIONS.values() for page in pages
]
NON_STAFF_RESTRICTED_PAGES: Final[list[str]] = [
    page for pages in NON_STAFF_PERMISSIONS.values() for page in pages
]
RESTRICTED_PAGES: Final[list[str]] = [
    *STAFF_RESTRICTED_PAGES,
    *NON_STAFF_RESTRICTED_PAGES,
]
