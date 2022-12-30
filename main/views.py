import logging
from logging import Logger
from typing import Any

from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect

from . import constants
from . import messages as MSG

logger: Logger = logging.getLogger(constants.LOGGERS.MAIN)


def index(request: HttpRequest) -> HttpResponse:
    if request.method == constants.POST_METHOD:
        UserName: str = request.POST.get('user_name')
        Password: str = request.POST.get('password')
        user: User = authenticate(
            request, username=UserName, password=Password)

        if user is not None:
            login(request, user)
            return redirect(constants.PAGES.INDEX_PAGE)
        else:
            MSG.INCORRECT_INFO(request)

    return render(request, constants.TEMPLATES.INDEX_TEMPLATE)


def about(request: HttpRequest) -> HttpResponse:
    return render(request, constants.TEMPLATES.ABOUT_TEMPLATE)


def logoutUser(request: HttpRequest) -> HttpResponse:
    try:
        logout(request)
    except AttributeError:
        pass
    return redirect(constants.PAGES.INDEX_PAGE)


def unauthorized(request: HttpRequest) -> HttpResponse:
    logger.warning(
        f"The user [{request.user}] is unauthorized to view this page")
    return render(request, constants.TEMPLATES.UNAUTHORIZED_TEMPLATE)
