import json
import logging
import os
from typing import Any, Final

from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.db import transaction
from django.db.models import OuterRef, Subquery, Sum
from django.db.models.query import QuerySet, Q, F
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpRequest, HttpResponse, Http404
from django.template.loader import get_template
from django.utils.timezone import datetime
from dateutil.relativedelta import relativedelta

from main import constants
from main import messages as MSG
from main.utils import Pagination, sendEmail, logUserActivity
from accounting.models import Account, Bond
from member.models import Person, Membership
from parameter.service import getParameterValue

from .filters import MembershipPaymentFilter
from .forms import MembershipPaymentForm
from .models import MembershipPayment


def membershipPaymentPage(request: HttpRequest) -> HttpResponse:
    form: MembershipPaymentForm = MembershipPaymentForm()
    head_img_url: str = getParameterValue(
        constants.PARAMETERS.MEMBERSHIP_TRANSFER_INFO_IMAGE)

    user_data: dict[str, Any] = Person.getUserData(request.user)
    membership: Membership = Membership.get(
        pk=int(user_data.get('membership_id')))
    from_month: datetime = datetime.strptime(
        membership.getNextPaymentStartMonth(), '%m/%Y')

    difference = relativedelta(datetime.now(), from_month)
    number_of_overdue_months: int = (difference.years * 12) + difference.months
    number_of_overdue_months = number_of_overdue_months if number_of_overdue_months > 0 else 0

    if request.method == constants.POST_METHOD:

        if membership.hasPendingPayment():
            MSG.HAS_PENDING_PAYMENT(request)
            context: dict[str, Any] = {
                'form': form, 'head_img_url': head_img_url,
                "number_of_overdue_months": number_of_overdue_months}
            return render(request, constants.TEMPLATES.MEMBERSHIP_PAYMENT_PAGE_TEMPLATE, context)

        MEMBERSHIP_COST_PER_MONTH: Final[float] = 50_000.00
        updated_data: dict[str, Any] = request.POST.copy()
        updated_data['membership'] = membership
        updated_data['amount'] = int(updated_data.get(
            'number_of_months')) * MEMBERSHIP_COST_PER_MONTH
        updated_data['from_month'] = membership.getNextPaymentStartMonth()

        form: MembershipPaymentForm = MembershipPaymentForm(
            updated_data, request.FILES)

        if form.is_valid():
            payment: MembershipPayment = form.save()
            MSG.PAYMENT_SENT(request)

            template = get_template(
                constants.TEMPLATES.MEMBERSHIP_PAYMENT_EMAIL_TEMPLATE)
            email: EmailMessage = EmailMessage(
                "شكرًا لتسديد اشتراكك العضوية في الجالية اليمنية بإندونيسيا",
                template.render({
                    "name": user_data['name_ar'],
                    "period": payment.period,
                    "payment_date": payment.created,
                    "amount": payment.amount,
                    "reference_number": payment.reference_number
                }),
                settings.EMAIL_HOST_USER,
                [f"{user_data['name_ar']} <{user_data['email']}>"],
            )
            email.content_subtype = 'html'
            email.fail_silently = False
            sendEmail(email)
            logUserActivity(request, constants.ACTION.ADD_MEMBERSHIP_PAYMENT,
                            f"دفع اشتراك {payment.period} من قِبل العضو {user_data['name_ar']}")

        return redirect(f"{reverse(constants.PAGES.MEMBERSHIP_PAYMENT_HISTORY_PAGE)}?last=")

    context: dict[str, Any] = {'form': form, 'head_img_url': head_img_url,
                               "number_of_overdue_months": number_of_overdue_months}
    return render(request, constants.TEMPLATES.MEMBERSHIP_PAYMENT_PAGE_TEMPLATE, context)


def membershipPaymentHistoryPage(request: HttpRequest) -> HttpResponse:
    user_data: dict[str, Any] = Person.getUserData(request.user)

    membership: Membership = Membership.get(
        pk=int(user_data.get('membership_id')))

    membership_issue_date = constants.MONTHS_AR[membership.issue_date.month -
                                                1] + " " + str(membership.issue_date.year)

    queryset: QuerySet[MembershipPayment] = membership.payments.prefetch_related()
    queryset = queryset.all().order_by('-id')

    if request.GET.get('last') is not None:
        queryset = queryset[:1]

    page: str = request.GET.get('page')
    pagination = Pagination(queryset, int(page) if page is not None else 1, 3)
    page_obj: QuerySet[Person] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    last_paid_month = membership.last_month_paid or None
    last_paid_month = constants.MONTHS_AR[int(
        last_paid_month.split('/')[0]) - 1] + " " + last_paid_month.split(
            '/')[1] if last_paid_month else "-"

    total_paid_amount = queryset.aggregate(
        total=Sum("amount", default=0, filter=Q(
            status=constants.PAYMENT_STATUS.APPROVED))).get("total")

    from_month: datetime = datetime.strptime(
        membership.getNextPaymentStartMonth(), '%m/%Y')

    difference = relativedelta(datetime.now(), from_month)
    number_of_overdue_months: int = (difference.years * 12) + difference.months
    number_of_overdue_months = number_of_overdue_months if number_of_overdue_months > 0 else 0

    MEMBERSHIP_COST_PER_MONTH: Final[float] = 50_000.00
    total_overdue_amount = number_of_overdue_months * MEMBERSHIP_COST_PER_MONTH

    temp_payment: MembershipPayment = MembershipPayment()
    temp_payment.from_month = membership.getNextPaymentStartMonth()
    temp_payment.number_of_months = number_of_overdue_months
    overdue_period = temp_payment.period if number_of_overdue_months > 0 else "-"

    context: dict[str, Any] = {'is_paginated': is_paginated, 'page_obj': page_obj,
                               'membership_issue_date': membership_issue_date,
                               "last_paid_month": last_paid_month, "total_paid_amount": total_paid_amount,
                               "number_of_overdue_months": number_of_overdue_months,
                               "total_overdue_amount": total_overdue_amount, "overdue_period": overdue_period,
                               }
    return render(request, constants.TEMPLATES.MEMBERSHIP_PAYMENT_HISTORY_PAGE_TEMPLATE, context)


def getReceipt(request: HttpRequest, reference_number: str) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect(constants.PAGES.UNAUTHORIZED_PAGE)
    try:
        pk: int = Person.getUserData(request.user).get('membership_id')
        if not pk:
            raise Http404
        payment: MembershipPayment = MembershipPayment.get(
            membership__id=pk, reference_number=reference_number)
    except MembershipPayment.DoesNotExist:
        raise Http404

    file_path = payment.receipt.path
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            extension: str = file_path.split('.')[-1]
            mime_type: str = constants.MIME_TYPE.JPEG
            if extension == 'png':
                mime_type = constants.MIME_TYPE.PNG

            response = HttpResponse(file.read(), content_type=mime_type)
            response['Content-Disposition'] = f'inline; filename={payment.reference_number}.{extension}'
            return response
    raise Http404


def membershipPaymentListPage(request: HttpRequest) -> HttpResponse:
    queryset: QuerySet[MembershipPayment] = MembershipPayment.objects.filter(
        ~Q(status=constants.PAYMENT_STATUS.PENDING)
    ).select_related('membership').annotate(
        member_name=Subquery(
            Person.objects.filter(
                membership=OuterRef('membership')).values('name_ar')[:1]
        )
    ).order_by('-updated')

    is_pending_list_empty: bool = not MembershipPayment.objects.filter(
        status=constants.PAYMENT_STATUS.PENDING
    ).exists()

    paymentFilter: MembershipPaymentFilter = MembershipPaymentFilter(
        request.GET, queryset=queryset)
    queryset = paymentFilter.qs

    page: str = request.GET.get('page')
    pagination = Pagination(queryset, int(page) if page is not None else 1)
    page_obj: QuerySet[MembershipPayment] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated
    context: dict[str, Any] = {'is_pending_list_empty': is_pending_list_empty, 'page_obj': page_obj,
                               'is_paginated': is_paginated, 'paymentFilter': paymentFilter}
    return render(request, constants.TEMPLATES.MEMBERSHIP_PAYMENT_LIST_PAGE_TEMPLATE, context)


def membershipPaymentPendingListPage(request: HttpRequest) -> HttpResponse:

    if request.method == constants.POST_METHOD:
        payment: MembershipPayment = get_object_or_404(
            MembershipPayment,
            pk=request.POST.get('pk'),
            status=constants.PAYMENT_STATUS.PENDING)

        try:
            number_of_months: int = int(request.POST.get('number_of_months'))
        except ValueError:
            MSG.SOMETHING_WRONG(request)
            return redirect(constants.PAGES.LOGOUT)

        if number_of_months != payment.number_of_months:
            payment.number_of_months = number_of_months
            payment.amount = number_of_months * 50_000

        email: EmailMessage = None
        person: Person = Person.get(membership=payment.membership)
        if "approve" in request.POST:
            payment.status = constants.PAYMENT_STATUS.APPROVED

            template = get_template(
                constants.TEMPLATES.MEMBERSHIP_PAYMENT_APPROVED_EMAIL_TEMPLATE)
            email: EmailMessage = EmailMessage(
                "إشعار بتأكيد الدفع - عضوية الجالية اليمنية",
                template.render({
                    "name": person.name_ar,
                    "period": payment.period,
                    "payment_date": payment.created,
                    "amount": payment.amount,
                    "note": request.POST.get('note'),
                    "reference_number": payment.reference_number
                }),
                settings.EMAIL_HOST_USER,
                [f"{person.name_ar} <{person.email}>"],
            )

        if "reject" in request.POST:
            payment.status = constants.PAYMENT_STATUS.REJECTED

            template = get_template(
                constants.TEMPLATES.MEMBERSHIP_PAYMENT_REJECTED_EMAIL_TEMPLATE)
            email: EmailMessage = EmailMessage(
                "إشعار برفض الدفع - عضوية الجالية اليمنية",
                template.render({
                    "name": person.name_ar,
                    "period": payment.period,
                    "payment_date": payment.created,
                    "amount": payment.amount,
                    "reference_number": payment.reference_number
                }),
                settings.EMAIL_HOST_USER,
                [f"{person.name_ar} <{person.email}>"],
            )

        if payment.status != constants.PAYMENT_STATUS.PENDING:
            roll_back: bool = False
            payment.note = request.POST.get('note')
            payment.updateMembershipLastMonthPaid()
            if payment.status == constants.PAYMENT_STATUS.APPROVED:
                with transaction.atomic():
                    try:
                        Bond.generatePaymentBond(payment)
                        payment.save()
                    except Account.DoesNotExist:
                        roll_back = True
                        transaction.set_rollback(rollback=True)
                        MSG.INVALID_DEFAULT_ACCOUNT(request, getParameterValue(
                            constants.PARAMETERS.DEFAULT_PAYMENT_ACCOUNT))
                    except Exception as error:
                        roll_back = True
                        transaction.set_rollback(rollback=True)
                        MSG.SOMETHING_WRONG(request)
                        MSG.ERROR_MESSAGE(request, str(error))
                        MSG.SCREENSHOT(request)
            else:
                payment.save()

            if not roll_back:
                email.content_subtype = 'html'
                email.fail_silently = False
                sendEmail(email)
                activity_status: str = ''
                if payment.status == constants.PAYMENT_STATUS.APPROVED:
                    MSG.PAYMENT_APPROVED(request)
                    activity_status: str = 'قبول'
                else:
                    MSG.PAYMENT_REJECTED(request)
                    activity_status: str = 'رفض'
                logUserActivity(request, constants.ACTION.CHECK_PAYMENT,
                                f"{activity_status} دفع الاشتراك رقم '{payment.reference_number}'"
                                f" من قِبل {request.user.get_full_name()}")

    queryset: QuerySet[MembershipPayment] = MembershipPayment.objects.filter(
        status=constants.PAYMENT_STATUS.PENDING
    ).select_related('membership').annotate(
        member_name=Subquery(
            Person.objects.filter(
                membership=OuterRef('membership')).values('name_ar')[:1]
        )
    ).order_by('-created')

    page: str = request.GET.get('page')
    pagination = Pagination(queryset, int(page) if page is not None else 1, 3)
    page_obj: QuerySet[Person] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated
    context: dict[str, Any] = {'page_obj': page_obj,
                               'is_paginated': is_paginated}
    return render(request, constants.TEMPLATES.MEMBERSHIP_PAYMENT_PENDING_LIST_PAGE_TEMPLATE, context)


def addMembershipPaymentsPage(request: HttpRequest) -> HttpResponse:
    form: MembershipPaymentForm = MembershipPaymentForm()

    if request.method == constants.POST_METHOD:
        membership: Membership = Membership.get(
            card_number=request.POST.get("membership_card"))

        if membership.hasPendingPayment():
            MSG.MEMBERSHIP_HAS_PENDING_PAYMENT(request)
            context: dict[str, Any] = {'form': form}
            return render(request, constants.TEMPLATES.ADD_MEMBERSHIP_PAYMENTS_PAGE_TEMPLATE, context)

        MEMBERSHIP_COST_PER_MONTH: Final[float] = 50_000.00
        updated_data: dict[str, Any] = request.POST.copy()
        updated_data['membership'] = membership
        updated_data['amount'] = int(updated_data.get(
            'number_of_months')) * MEMBERSHIP_COST_PER_MONTH
        updated_data['from_month'] = membership.getNextPaymentStartMonth()

        form: MembershipPaymentForm = MembershipPaymentForm(
            updated_data, request.FILES)

        if form.is_valid():
            with transaction.atomic():
                payment: MembershipPayment = form.save()
                payment.status = constants.PAYMENT_STATUS.APPROVED
                payment.note = request.POST.get('note')
                payment.updateMembershipLastMonthPaid()
                try:
                    Bond.generatePaymentBond(payment)
                    payment.save()
                    template = get_template(
                        constants.TEMPLATES.MEMBERSHIP_PAYMENT_APPROVED_EMAIL_TEMPLATE)
                    person: Person = Person.get(membership=payment.membership)
                    email: EmailMessage = EmailMessage(
                        "إشعار بتأكيد الدفع - عضوية الجالية اليمنية",
                        template.render({
                            "name": person.name_ar,
                            "period": payment.period,
                            "payment_date": payment.created,
                            "amount": payment.amount,
                            "note": request.POST.get('note'),
                            "reference_number": payment.reference_number
                        }),
                        settings.EMAIL_HOST_USER,
                        [f"{person.name_ar} <{person.email}>"],
                    )
                    email.content_subtype = 'html'
                    email.fail_silently = False
                    sendEmail(email)
                    MSG.PAYMENT_REGISTERED(request)
                    logUserActivity(request, constants.ACTION.CHECK_PAYMENT,
                                    f"تسجيل دفع الاشتراك رقم '{payment.reference_number}'"
                                    f" من قِبل {request.user.get_full_name()}")

                    cache.delete(
                        f'NEXT_MEMBER_PAYMENT_START_MONTH:{membership.card_number}')
                    return redirect(constants.PAGES.MEMBERSHIP_PAYMENT_LIST_PAGE)
                except Account.DoesNotExist:
                    transaction.set_rollback(rollback=True)
                    MSG.INVALID_DEFAULT_ACCOUNT(request, getParameterValue(
                        constants.PARAMETERS.DEFAULT_PAYMENT_ACCOUNT))
                except Exception as error:
                    transaction.set_rollback(rollback=True)
                    MSG.SOMETHING_WRONG(request)
                    MSG.ERROR_MESSAGE(request, str(error))
                    MSG.SCREENSHOT(request)

    context: dict[str, Any] = {'form': form}
    return render(request, constants.TEMPLATES.ADD_MEMBERSHIP_PAYMENTS_PAGE_TEMPLATE, context)


def getPaymentPeriod(request: HttpRequest, pk: str, number_of_months: str) -> HttpResponse:
    payment: MembershipPayment = None
    if request.user.is_staff:
        if pk.startswith(getParameterValue(constants.PARAMETERS.THREE_CHARACTER_PREFIX_FOR_MEMBERSHIP)):
            if not cache.get('NEXT_MEMBER_PAYMENT_START_MONTH:' + str(pk)):
                membership: Membership = Membership.get(card_number=pk)
                cache.set('NEXT_MEMBER_PAYMENT_START_MONTH:' + str(pk),
                          membership.getNextPaymentStartMonth(), 120)  # 120 = 2 minutes

            payment = MembershipPayment()
            payment.from_month = cache.get(
                'NEXT_MEMBER_PAYMENT_START_MONTH:' + str(pk))
        else:
            payment = get_object_or_404(MembershipPayment, pk=pk)
    else:
        if not cache.get('NEXT_MEMBER_PAYMENT_START_MONTH:' + str(request.user.id)):
            user_data: dict[str, Any] = Person.getUserData(request.user)
            membership: Membership = Membership.get(
                pk=int(user_data.get('membership_id')))
            cache.set('NEXT_MEMBER_PAYMENT_START_MONTH:' + str(request.user.id),
                      membership.getNextPaymentStartMonth(), 120)  # 120 = 2 minutes

        payment = MembershipPayment()
        payment.from_month = cache.get(
            'NEXT_MEMBER_PAYMENT_START_MONTH:' + str(request.user.id))

    payment.number_of_months = int(number_of_months)
    MEMBERSHIP_COST_PER_MONTH: Final[float] = 50_000.00
    amount: float = payment.number_of_months * MEMBERSHIP_COST_PER_MONTH
    response_data = {'period': payment.period, 'amount': amount}
    json_data = json.dumps(response_data, ensure_ascii=False).encode('utf-8')
    return HttpResponse(json_data, content_type='application/json; charset=utf-8')
