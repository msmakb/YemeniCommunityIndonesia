import logging
from typing import Any

from django.core.cache import cache
from django.http import HttpRequest
from django.contrib.auth.models import Group, User

from . import constants
from .models import AuditEntry
from .utils import getClientIp, getUserAgent

from parameter.service import getParameterValue

logger = logging.getLogger(constants.LOGGERS.MAIN)


def createGroups(**kwargs) -> None:
    groups: list[str] = Group.objects.all().values_list('name', flat=True)
    for group in groups:
        if group not in constants.GROUPS:
            Group.objects.get(name=group).delete()
            print(f"  {group} group was deleted.")

    for group in constants.GROUPS:
        if group not in groups:
            obj: Group = Group.objects.create(name=group)
            print(f"  {obj.name} group was created.")

    logger.info("All default groups up to date.")


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

    CLIENT_FAILED_LOGIN_ATTEMPT_CACHE_KEY: str = "FAIL_LOGIN:%s" % ip
    current_client_failed_attempts: int | None = cache.get(
        CLIENT_FAILED_LOGIN_ATTEMPT_CACHE_KEY)
    if current_client_failed_attempts:
        current_client_failed_attempts += 1
    else:
        current_client_failed_attempts = 1

    cache.set(
        CLIENT_FAILED_LOGIN_ATTEMPT_CACHE_KEY,
        current_client_failed_attempts,
        constants.DEFAULT_CACHE_EXPIRE * getParameterValue(
            constants.PARAMETERS.ALLOWED_LOGGED_IN_ATTEMPTS_RESET)
    )

    AuditEntry.create(action=constants.ACTION.LOGGED_FAILED,
                      user_agent=getUserAgent(request),
                      ip=ip,
                      username=credentials.get('username', None))
    logger.warning(f'Failed accessed to login using: {credentials}')
