import logging
from logging import Logger
from typing import Any
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.utils import timezone

from . import constants
from . import messages as MSG
from .decorators import isAuthenticatedUser
from .models import AuditEntry
from .parameters import getParameterValue
from .utils import getClientIp

logger: Logger = logging.getLogger(constants.LOGGERS.MAIN)


@isAuthenticatedUser
def index(request: HttpRequest) -> HttpResponse:
    return render(request, constants.TEMPLATES.INDEX_TEMPLATE)


@isAuthenticatedUser
def loginPage(request: HttpRequest) -> HttpResponse:
    if request.method == constants.POST_METHOD:
        UserName: str = request.POST.get('user_name')
        Password: str = request.POST.get('password')
        user: User = auth.authenticate(
            request, username=UserName, password=Password)

        if user is not None:
            auth.login(request, user)
            return redirect(constants.PAGES.INDEX_PAGE)
        else:
            MSG.INCORRECT_INFO(request)
            allowed_attempts: int = getParameterValue(constants.PARAMETERS.ALLOWED_LOGGED_IN_ATTEMPTS)
            failed_login_count: int = AuditEntry.getLastAuditEntry().filter(
                action=constants.ACTION.LOGGED_FAILED,
                ip=getClientIp(request)
            ).count()
            if failed_login_count > abs(allowed_attempts / failed_login_count):
                MSG.MANY_FAILED_LOGIN_WARNING(request)

    return render(request, constants.TEMPLATES.LOGIN_TEMPLATE)


def membershipTerms(request: HttpRequest) -> HttpResponse:
    return render(request, constants.TEMPLATES.MEMBERSHIP_TERMS_TEMPLATE)


def about(request: HttpRequest) -> HttpResponse:
    return render(request, constants.TEMPLATES.ABOUT_TEMPLATE)


def logoutUser(request: HttpRequest) -> HttpResponse:
    try:
        auth.logout(request)
    except AttributeError:
        pass
    return redirect(constants.PAGES.LOGIN_PAGE)


def unauthorized(request: HttpRequest) -> HttpResponse:
    logger.warning(
        f"The user [{request.user}] is unauthorized to view this page")
    return render(request, constants.TEMPLATES.UNAUTHORIZED_TEMPLATE)
