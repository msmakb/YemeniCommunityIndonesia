from typing import Callable, Final

from django.contrib import messages
from django.http import HttpRequest

BLOCK_WARNING: Final[Callable[[HttpRequest], None]] = lambda request: messages.warning(
    request, "تحذير!! لقد قمت بإرسال العديد من الرسائل "
    + "العشوائية إلى النظام ، فكن حذرًا وإلا فسيتم حظرك في المرة القادمة.")
INCORRECT_INFO: Final[Callable[[HttpRequest], None]] = lambda request: messages.error(
    request, "اسم المستخدم أو كلمة المرور غير صحيحة، أو أن عضويتك قيد المعالجة من قِبَل الإدارة")
SOMETHING_WRONG: Final[Callable[[HttpRequest], None]] = lambda request: messages.warning(
    request, "عفوًا!! هناك خطأ ما...")
TIME_OUT: Final[Callable[[HttpRequest], None]] = lambda request: messages.info(
    request, "انقضت مهلة جلستك. الرجاد الدخول على الحساب من جديد")
TERMS_MUST_AGREE: Final[Callable[[HttpRequest], None]] = lambda request: messages.error(
    request, "إذا كنت ترغب في أن تصبح عضوًا ، يجب أن توافق على جميع شروط العضوية")
PASSPORT_NUMBER_ERROR: Final[Callable[[HttpRequest], None]] = lambda request: messages.error(
    request, "يجب عليك إدخال رقم جواز السفر الصحيح لتأكيد السجل ، أو إدخال معرف السجل الصحيح للرفض")
PASSPORT_NUMBER_EXISTS: Final[Callable[[HttpRequest], None]] = lambda request: messages.error(
    request, "رقم جواز السفر الذي أدخلته مسجل بالفعل في قاعدة البيانات،"
    + " يرجى التأكد من تسجيل هذا الشخص من قبل أو التأكد من صحة الرقم الذي أدخلته")
MEMBERSHIP_FORM_POST_LIMIT: Final[Callable[[HttpRequest], None]] = lambda request: messages.warning(
    request, "لقد وصلت إلى الحد الأقصى لعدد الإدخالات لهذا النموذج ، يرجى المحاولة مرة أخرى في وقت لاحق")
ACCEPT_MEMBERSHIP: Final[Callable[[HttpRequest], None]] = lambda request: messages.error(
    request, "الرجاء الموافقة على العضوية واختيار نوعها لإنشاء بطاقة عضوية جديدة")
MEMBERSHIP_MUST_GENERATED: Final[Callable[[HttpRequest], None]] = lambda request: messages.error(
    request, "يجب إنشاء بطاقة العضو أولاً للموافقة على العضوية")
FIX_ERRORS: Final[Callable[[HttpRequest], None]] = lambda request: messages.error(
    request, "الرجاء تصحيح الاخطاء الواردة أدناه")
NO_DATA: Final[Callable[[HttpRequest], None]] = lambda request: messages.warning(
    request, "لا توجد بيانات لاستخراجها")
SCREENSHOT: Final[Callable[[HttpRequest], None]] = lambda request: messages.info(
    request, "يرجى أخذ لقطة شاشة وإرسالها إلى المطور")
ERROR_MESSAGE: Final[Callable[[HttpRequest, str], None]] = lambda request, message: messages.error(
    request, message)
