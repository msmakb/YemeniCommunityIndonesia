from typing import Callable, Final

from django.contrib import messages
from django.http import HttpRequest

BLOCK_WARNING: Final[Callable[[HttpRequest], None]] = lambda request: messages.warning(
    request, "تحذير!! لقد قمت بإرسال العديد من الرسائل "
    + "العشوائية إلى النظام ، فكن حذرًا وإلا فسيتم حظرك في المرة القادمة.")
INCORRECT_INFO: Final[Callable[[HttpRequest], None]] = lambda request: messages.error(
    request, "اسم المستخدم أو كلمة المرور غير صحيحة")
SOMETHING_WRONG: Final[Callable[[HttpRequest], None]] = lambda request: messages.warning(
    request, "عفوًا!! هناك خطأ ما...")
TIME_OUT: Final[Callable[[HttpRequest], None]] = lambda request: messages.info(
    request, "انقضت مهلة جلستك. الرجاد الدخول على الحساب من جديد")
TERMS_MUST_AGREE: Final[Callable[[HttpRequest], None]] = lambda request: messages.error(
    request, "إذا كنت ترغب في أن تصبح عضوًا ، يجب أن توافق على جميع شروط العضوية")
