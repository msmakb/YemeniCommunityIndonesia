from typing import Callable, Final

from django.contrib import messages
from django.http import HttpRequest
from django.urls import reverse

from main.constants import PAGES

BLOCK_WARNING: Final[Callable[[HttpRequest], None]] = lambda request: messages.warning(
    request, "تحذير!! لقد قمت بإرسال العديد من الرسائل "
    + "العشوائية إلى النظام ، فكن حذرًا وإلا فسيتم حظرك في المرة القادمة.")
INCORRECT_INFO: Final[Callable[[HttpRequest], None]] = lambda request: messages.error(
    request, "اسم المستخدم أو كلمة المرور غير صحيحة، أو أن عضويتك قيد المعالجة من قِبَل الإدارة")
MANY_FAILED_LOGIN_WARNING: Final[Callable[[HttpRequest], None]] = lambda request: messages.warning(
    request, "تنبيه: تم تكرار محاولات تسجيل الدخول الفاشلة بشكل متكرر. الرجاء التحقق من صحة المعلومات "
    + "وتجنب المحاولات غير المصرح بها. سيتم حظرك بعد 5 محاولات فاشلة. للمساعدة، يرجى التواصل مع الدعم الفني.")
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
MEMBER_FORM_CLOSE: Final[Callable[[HttpRequest], None]] = lambda request: messages.info(
    request, "رابط التسجيل للعضوية مغلق في الوقت الحالي. يرجى العودة لاحقاً")
APPROVE_RECORD: Final[Callable[[HttpRequest], None]] = lambda request: messages.success(
    request, "تم قبول السجل بنجاح")
REJECT_RECORD: Final[Callable[[HttpRequest], None]] = lambda request: messages.success(
    request, "تم رفض السجل بنجاح")
DONATION_LIMIT: Final[Callable[[HttpRequest], None]] = lambda request: messages.error(
    request, "لأسباب أمنية، نقيد عدد التبرعات التي يمكنك إرسالها بحد أقصى 5 تبرعات في اليوم")

# ==== Broadcast App Messages ====
ADD_BROADCAST: Final[Callable[[HttpRequest, str], None]] = lambda request: messages.success(
    request, "تم إضافة البرودكاست بنجاح")
UPDATE_BROADCAST: Final[Callable[[HttpRequest, str], None]] = lambda request: messages.success(
    request, "تم تعديل البرودكاست بنجاح")
ADD_ATTACHMENT: Final[Callable[[HttpRequest, str], None]] = lambda request: messages.success(
    request, "تم إضافة المُرفق بنجاح")
DELETE_ATTACHMENT: Final[Callable[[HttpRequest, str], None]] = lambda request: messages.success(
    request, "تم إزالة الملف بنجاح")

# ==== Parameter App Messages ====
PAGE_REQUIRE_RE_LOGIN: Final[Callable[[HttpRequest], None]] = lambda request: messages.info(
    request, "الرجاء إعادة تسجيل الدخول لعرض محتوى هذه الصفحة")

# ==== Company User App Messages ====
ADD_ROLE: Final[Callable[[HttpRequest], None]] = lambda request: messages.success(
    request, "تم إضافة الوظيفة بنجاح")
UPDATE_ROLE: Final[Callable[[HttpRequest], None]] = lambda request: messages.success(
    request, "تم تعديل الوظيفة بنجاح")
DELETE_ROLE: Final[Callable[[HttpRequest], None]] = lambda request: messages.success(
    request, "تم حذف الوظيفة بنجاح")
ADD_USER: Final[Callable[[HttpRequest], None]] = lambda request: messages.success(
    request, "تم إضافة المستخدم بنجاح")
UPDATE_USER: Final[Callable[[HttpRequest], None]] = lambda request: messages.success(
    request, "تم تعديل المستخدم بنجاح")
DELETE_USER: Final[Callable[[HttpRequest], None]] = lambda request: messages.success(
    request, "تم إزالة المستخدم بنجاح")
USER_REGISTRATION_DONE: Final[Callable[[HttpRequest], None]] = lambda request: messages.success(
    request, f'تم إكمال تسجيلك. يمكنك المضي قدمًا و <a href="{reverse(PAGES.LOGIN_PAGE)}" '
    + 'style="text-decoration:none;"><b>تسجيل الدخول</b></a> الآن')
PROTECTED_ROLE: Final[Callable[[HttpRequest], None]] = lambda request: messages.error(
    request, "تعذر حذف الوظيفة لأنها مرتبطة ببعض العناصر الأخرى في النظام")

# ==== Company User App Messages ====
HAS_PENDING_PAYMENT: Final[Callable[[HttpRequest], None]] = lambda request: messages.error(
    request, "يوجد لديك دفع معلقة. يرجى الانتظار حتى يتم معالجتها أولاً")
PAYMENT_SENT: Final[Callable[[HttpRequest], None]] = lambda request: messages.success(
    request, "شكرا لكم على دفع رسوم العضوية. ستتم معالجة مدفوعات الاشتراك المرسلة وإخطارها لاحقًا")
PAYMENT_APPROVED: Final[Callable[[HttpRequest], None]] = lambda request: messages.success(
    request, "تم قبول الدفع بنجاح")
PAYMENT_REJECTED: Final[Callable[[HttpRequest], None]] = lambda request: messages.success(
    request, "تم رفض الدفع بنجاح")

# ==== Accounting App Messages ====
ADD_ACCOUNT: Final[Callable[[HttpRequest, str], None]] = lambda request: messages.success(
    request, "تم إضافة الحساب بنجاح")
UPDATE_ACCOUNT: Final[Callable[[HttpRequest, str], None]] = lambda request: messages.success(
    request, "تم تعديل الحساب بنجاح")
