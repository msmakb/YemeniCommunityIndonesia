import logging
from typing import Any

from django.conf import settings
from django.http import HttpRequest
from django.contrib.auth.models import Group, User

from . import constants
from .models import AuditEntry
from .utils import getClientIp, getUserAgent

logger = logging.getLogger(constants.LOGGERS.MAIN)


def createGroups(**kwargs) -> None:
    if not Group.objects.all().exists():
        for name in constants.GROUPS:
            group = Group.objects.create(name=name)
            print(f"  {group} group was created.")
        logger.info("All default groups was successfully created.")
        user: User = User.objects.create_superuser(
            username="admin",
            password=settings.SP)
        Group.objects.get(name=constants.GROUPS.MANAGER).user_set.add(user)


def userLoggedIn(sender: User, request: HttpRequest, user: User, **kwargs):
    ip: str = getClientIp(request)
    AuditEntry.create(action=constants.ACTION.LOGGED_IN,
                      user_agent=getUserAgent(request),
                      ip=ip,
                      username=user.username)
    logger.info(f'Login user: {user} via ip: {ip}')


def userLoggedOut(sender: User, request: HttpRequest, user: User, **kwargs):
    ip: str = getClientIp(request)
    AuditEntry.create(action=constants.ACTION.LOGGED_OUT,
                      user_agent=getUserAgent(request),
                      ip=ip,
                      username=user.username)
    logger.info(f'Logout user: {user} via ip: {ip}')


def userLoggedFailed(sender, credentials: dict[str, Any], **kwargs):
    request: HttpRequest = kwargs.get('request')
    ip: str = getClientIp(request)
    AuditEntry.create(action=constants.ACTION.LOGGED_FAILED,
                      user_agent=getUserAgent(request),
                      ip=ip,
                      username=credentials.get('username', None))
    logger.warning(f'Failed accessed to login using: {credentials}')
