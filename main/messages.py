from typing import Callable, Final

from django.contrib import messages
from django.http import HttpRequest

"""============================= Main Messages ============================="""
BLOCK_WARNING: Final[Callable[[HttpRequest], None]] = lambda request: messages.warning(
    request, "WARNING!! The system logged you out for spamming, "
    + "next time you will be blocked")
INCORRECT_INFO: Final[Callable[[HttpRequest], None]] = lambda request: messages.error(
    request, "اسم المستخدم أو كلمة المرور غير صحيحة")
SOMETHING_WRONG: Final[Callable[[HttpRequest], None]] = lambda request: messages.warning(
    request, "Ops!! something went wrong...")
TIME_OUT: Final[Callable[[HttpRequest], None]] = lambda request: messages.info(
    request, "انقضت مهلة جلستك. الرجاد الدخول على الحساب من جديد")
