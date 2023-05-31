import logging
from logging import Logger
from typing import Any, Callable

from django.http import HttpRequest
from django.shortcuts import redirect

from . import constants

logger: Logger = logging.getLogger(constants.LOGGERS.MAIN)


def _getRequestFromViewArgs(args: list[Any]) -> HttpRequest:
    request: HttpRequest = None
    for arg in args:
        if isinstance(arg, HttpRequest):
            request = arg
    if not request:
        raise TypeError("This is not a view function!")
    else:
        return request


def isAuthenticatedUser(view_func: Callable) -> Callable:
    def wrapper_func(*args, **kwargs) -> Callable:
        request: HttpRequest = _getRequestFromViewArgs(args)
        if request.user.is_authenticated:
            logger.info(
                f"The user [{request.user.username}] is authenticated")
            if request.user.is_staff:
                return redirect(constants.PAGES.STAFF_DASHBOARD)
            else:
                return redirect(constants.PAGES.MEMBER_DASHBOARD)
        else:
            return view_func(*args, **kwargs)
    return wrapper_func
