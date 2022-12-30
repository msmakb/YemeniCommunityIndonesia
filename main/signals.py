import logging
from typing import Any

from django.http import HttpRequest
from django.contrib.auth.models import User

from . import constants
from .models import AuditEntry
from .utils import getClientIp, getUserAgent

logger = logging.getLogger(constants.LOGGERS.MAIN)


def createParameters(**kwargs):
    from .parameters import _saveDefaultParametersToDataBase
    _saveDefaultParametersToDataBase()
    logger.info("All default parameters was successfully created.")


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
