import logging
from logging import Logger
from typing import Any, Callable

from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import resolve

from . import constants
from . import messages as MSG
from .utils import getUserGroupe

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
            if request.user.groups.exists():
                group: str = getUserGroupe(request)
                match group:
                    case constants.GROUPS.MANAGER:
                        return redirect(constants.PAGES.DASHBOARD, "list")
                    case constants.GROUPS.MEMBER:
                        return redirect(constants.PAGES.MEMBER_PAGE, request.user.id)
                    case _:
                        return redirect(constants.PAGES.LOGOUT)
            else:
                logger.warning("The user has no groups!!")
                MSG.SOMETHING_WRONG(request)
                return redirect(constants.PAGES.LOGOUT)
        else:
            return view_func(*args, **kwargs)
    return wrapper_func
