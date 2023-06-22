from typing import Any

from django.core.cache import cache
from django.db.models.query import QuerySet, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from main import constants
from main.models import AuditEntry, BlockedClient
from main.utils import Pagination


def monitorPage(request: HttpRequest) -> HttpResponse:
    context: dict[str, Any] | None = cache.get("CACHED_PAGE_CONTEXT:MONITOR")
    if context:
        return render(request, constants.TEMPLATES.MONITOR_PAGE_TEMPLATE, context)

    months_filter: list[str] = []
    months_labels: list[str] = []

    submit_form_data: list[str] = []
    first_visits_data: list[str] = []

    year: int = timezone.datetime.now().year
    temp: timezone.datetime = None
    for i in range(6):
        temp = timezone.datetime.now() - timezone.timedelta(days=30 * i)
        months_filter.append(
            (str(year) + '-' + str(temp.month).rjust(2, '0') + '-'))
        months_labels.append(constants.MONTHS_AR[temp.month - 1])

        if temp.month == 1:
            year -= 1

    months_filter.reverse()
    months_labels.reverse()

    for month_filter in months_filter:
        submit_form_data.append(AuditEntry.countFiltered(
            created__contains=month_filter,
            action=constants.ACTION.MEMBER_FORM_POST))
        first_visits_data.append(AuditEntry.countFiltered(
            created__contains=month_filter,
            action=constants.ACTION.FIRST_VISIT))

    sus_count: int = AuditEntry.countFiltered(
        action__in=[
            constants.ACTION.SUSPICIOUS_POST,
            constants.ACTION.ATTACK_ATTEMPT
        ]
    )

    failed_login_attempt_count: int = AuditEntry.countFiltered(
        action=constants.ACTION.LOGGED_FAILED,
        created__gt=timezone.datetime.now() - timezone.timedelta(days=30)
    )

    blocked_devices_count: int = BlockedClient.countFiltered(
        ~Q(block_type=constants.BLOCK_TYPES.UNBLOCKED)
    )

    context = {
        'sus_count': sus_count,
        'months_labels': months_labels,
        'submit_form_data': submit_form_data,
        'first_visits_data': first_visits_data,
        'failed_login_attempt_count': failed_login_attempt_count,
        'blocked_devices_count': blocked_devices_count,
    }

    cache.set("CACHED_PAGE_CONTEXT:MONITOR", context,
              constants.DEFAULT_CACHE_EXPIRE)
    return render(request, constants.TEMPLATES.MONITOR_PAGE_TEMPLATE, context)


def activityLogPage(request: HttpRequest) -> HttpResponse:
    queryset: QuerySet[AuditEntry] = AuditEntry.filter(
        ~Q(action__in=[
            constants.ACTION.NORMAL_POST,
            constants.ACTION.ATTACK_ATTEMPT,
            constants.ACTION.SUSPICIOUS_POST
        ]),
        created__gt=timezone.datetime.now() - timezone.timedelta(days=30)
    ) | AuditEntry.filter(
        action__in=[
            constants.ACTION.ATTACK_ATTEMPT,
            constants.ACTION.SUSPICIOUS_POST
        ]
    ).order_by('-created')

    activity_filter: str = request.GET.get('activity-filter')
    if request.GET.get('activity-filter'):
        if activity_filter == '5':
            queryset = queryset.filter(action__in=[activity_filter, '6'])
        else:
            queryset = queryset.filter(action=activity_filter)

    page: str = request.GET.get('page')
    pagination = Pagination(queryset, int(page) if page is not None else 1,
                            paginate_by=15)
    page_obj: QuerySet[AuditEntry] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    activities: dict[str, str] = {
        k: constants.ACTION_STR_AR[int(k)] for k in constants.ACTION}

    del activities['4']
    del activities['6']
    del activities['8']
    del activities['9']

    context: dict[str, Any] = {'activities': activities, 'page_obj': page_obj,
                               'is_paginated': is_paginated}
    return render(request, constants.TEMPLATES.ACTIVITY_LOG_PAGE_TEMPLATE, context)


def blockListPage(request: HttpRequest) -> HttpResponse:
    queryset: QuerySet[AuditEntry] = BlockedClient.getAllOrdered(
        'created', reverse=True)
    page: str = request.GET.get('page')
    pagination = Pagination(queryset, int(page) if page is not None else 1,
                            paginate_by=15)
    page_obj: QuerySet[AuditEntry] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context: dict[str, Any] = {
        'page_obj': page_obj, 'is_paginated': is_paginated}
    return render(request, constants.TEMPLATES.BLOCK_LIST_PAGE_TEMPLATE, context)
