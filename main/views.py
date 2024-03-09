import logging
from logging import Logger
from typing import Any

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.contrib import auth
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models.query import QuerySet
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect

from . import constants
from . import messages as MSG
from .decorators import isAuthenticatedUser
from .models import Donation
from .utils import Pagination, getClientIp, logUserActivity

from parameter.service import getParameterValue
from accounting.models import Account, Bond

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
            max_allowed_attempts: int = getParameterValue(
                constants.PARAMETERS.ALLOWED_LOGGED_IN_ATTEMPTS)
            failed_login_attempts: int | None = cache.get(
                "FAIL_LOGIN:%s" % getClientIp(request))
            if not failed_login_attempts:
                failed_login_attempts = 0

            if failed_login_attempts > abs(max_allowed_attempts / 2):
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


def donation(request: HttpRequest) -> HttpResponse:
    errors: dict[str, str] = {}
    head_img_url: str = getParameterValue(
        constants.PARAMETERS.MEMBERSHIP_TRANSFER_INFO_IMAGE)

    if request.method == constants.POST_METHOD:
        try:
            donation: Donation = Donation()
            donation.name = request.POST.get(
                "name") if request.POST.get("name") else 'فاعل خير'
            donation.amount = request.POST.get(
                "amount") if request.POST.get("amount") else None
            donation.receipt = request.FILES.get(
                "receipt") if request.FILES.get("receipt") else None
            donation.clean_fields()
            donation.save()

            cache.set('DONATION_FROM_IP:' + getClientIp(request), '', 300)
            logUserActivity(request, constants.ACTION.DONATION,
                            f"تبرع من '{donation.name}'")
            return redirect(constants.PAGES.THANKS_FOR_DONATION_PAGE)

        except ValidationError as e:
            errors = e.message_dict

    context: dict[str, Any] = {'head_img_url': head_img_url, 'errors': errors}
    return render(request, constants.TEMPLATES.DONATION_TEMPLATE, context)


def thanksForDonation(request: HttpRequest) -> HttpResponse:
    if 'DONATION_FROM_IP:' + getClientIp(request) not in cache:
        return redirect(constants.PAGES.INDEX_PAGE)

    return render(request, constants.TEMPLATES.THANKS_FOR_DONATION_TEMPLATE)


def donationListPage(request: HttpRequest) -> HttpResponse:
    queryset: QuerySet[Donation] = Donation.getAllOrdered(
        'created', reverse=True)

    if request.method == constants.POST_METHOD:
        print(request.POST)
        approved: bool | None = None
        if "approve" in request.POST:
            approved = True
        elif "reject" in request.POST:
            approved = False

        for donation in queryset:
            if f"ID-{donation.pk}" in request.POST and approved is not None:
                donation.is_valid_donation = approved
                with transaction.atomic():
                    donation.save()
                    try:
                        Bond.generateDonationBond(donation)
                        logUserActivity(request, constants.ACTION.VALIDATE_DONATION,
                                        f"التحقق من فاتورة التبرع رقم '{donation.pk}'"
                                        f" من قِبل {request.user.get_full_name()}")
                    except Account.DoesNotExist:
                        donation.created = donation.updated
                        transaction.set_rollback(rollback=True)
                        MSG.INVALID_DEFAULT_ACCOUNT(request, getParameterValue(
                            constants.PARAMETERS.DEFAULT_PAYMENT_ACCOUNT))
                    except Exception as error:
                        donation.created = donation.updated
                        transaction.set_rollback(rollback=True)
                        MSG.SOMETHING_WRONG(request)
                        MSG.ERROR_MESSAGE(request, str(error))
                        MSG.SCREENSHOT(request)

    page: str = request.GET.get('page')
    pagination = Pagination(queryset, int(page) if page is not None else 1)
    page_obj: QuerySet[Donation] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated
    context: dict[str, Any] = {'is_paginated': is_paginated,
                               'page_obj': page_obj}
    return render(request, constants.TEMPLATES.DONATION_LIST_PAGE_TEMPLATE, context)
