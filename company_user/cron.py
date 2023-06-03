from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.utils import timezone

from main import constants
from main.utils import logUserActivity


def cleanupInactiveStaffUsers():
    users: QuerySet[User] = User.objects.filter(
        is_staff=True,
        is_active=False,
        last_login__isnull=True,
        date_joined__lt=timezone.now() - timezone.timedelta(hours=1)
    )
    if users:
        users.delete()
        for user in users:
            logUserActivity(None, constants.ACTION.DELETE_USER,
                            f"حذف المستخدم ({user.get_full_name()}) "
                            + f"من قِبل النظام")
