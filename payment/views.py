import json
import logging
import os
from typing import Any, Final

from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.db.models import OuterRef, Subquery
from django.db.models.query import QuerySet, Q
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpRequest, HttpResponse, Http404
from django.template.loader import get_template

from main import constants
from main import messages as MSG
from main.utils import Pagination, sendEmail, logUserActivity
from member.models import Person, Membership
from parameter.service import getParameterValue

from .filters import MembershipPaymentFilter
from .forms import MembershipPaymentForm
from .models import MembershipPayment


def membershipPaymentPage(request: HttpRequest) -> HttpResponse:
    form: MembershipPaymentForm = MembershipPaymentForm()
    head_img_url: str = getParameterValue(
        constants.PARAMETERS.MEMBERSHIP_TRANSFER_INFO_IMAGE)

    if request.method == constants.POST_METHOD:
        user_data: dict[str, Any] = Person.getUserData(request.user)
        membership: Membership = Membership.get(
            pk=int(user_data.get('membership_id')))

        if membership.hasPendingPayment():
            MSG.HAS_PENDING_PAYMENT(request)
            context: dict[str, Any] = {
                'form': form, 'head_img_url': head_img_url}
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

    context: dict[str, Any] = {'form': form, 'head_img_url': head_img_url}
    return render(request, constants.TEMPLATES.MEMBERSHIP_PAYMENT_PAGE_TEMPLATE, context)


def membershipPaymentHistoryPage(request: HttpRequest) -> HttpResponse:
    user_data: dict[str, Any] = Person.getUserData(request.user)
    logger = logging.getLogger(constants.LOGGERS.MAIN)

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

    context: dict[str, Any] = {'is_paginated': is_paginated, 'page_obj': page_obj,
                               'membership_issue_date': membership_issue_date}
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
            MSG.PAYMENT_APPROVED(request)

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
            MSG.PAYMENT_REJECTED(request)

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
            payment.note = request.POST.get('note')
            payment.updateMembershipLastMonthPaid()
            payment.save()
            email.content_subtype = 'html'
            email.fail_silently = False
            sendEmail(email)
            activity_status: str = 'قبول' if payment.status == constants.PAYMENT_STATUS.APPROVED else 'رفض'
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


def getPaymentPeriod(request: HttpRequest, pk: str, number_of_months: str) -> HttpResponse:
    payment: MembershipPayment = None
    if request.user.is_staff:
        payment = get_object_or_404(MembershipPayment, pk=pk)
    else:
        if not cache.get('NEXT_MEMBER_PAYMENT_START_MONTH:' + str(request.user.id)):
            print("the user next payment start month not cached!!")
            user_data: dict[str, Any] = Person.getUserData(request.user)
            membership: Membership = Membership.get(
                pk=int(user_data.get('membership_id')))
            cache.set('NEXT_MEMBER_PAYMENT_START_MONTH:' + str(request.user.id),
                      membership.getNextPaymentStartMonth(), 120)  # 120 = 2 minutes

        payment = MembershipPayment()
        payment.from_month = cache.get(
            'NEXT_MEMBER_PAYMENT_START_MONTH:' + str(request.user.id))

    payment.number_of_months = int(number_of_months)
    response_data = {'period': payment.period}
    json_data = json.dumps(response_data, ensure_ascii=False).encode('utf-8')
    return HttpResponse(json_data, content_type='application/json; charset=utf-8')
