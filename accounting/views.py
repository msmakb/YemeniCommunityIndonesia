from typing import Any, Callable

from django.core.exceptions import EmptyResultSet
from django.db.models import Sum
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render, redirect, get_object_or_404

from main import constants
from main import messages as MSG
from main.utils import Pagination, logUserActivity, exportAsCsvExcel

from .filters import BondFilter
from .forms import AccountForm
from .models import Account, Bond


def accountingPage(request: HttpRequest) -> HttpResponse:
    context: dict[str, Any] = {}
    return render(request, constants.TEMPLATES.ACCOUNTING_PAGE_TEMPLATE, context)

def bondListPage(request: HttpRequest) -> HttpResponse:
    queryset: QuerySet[Bond] = Bond.objects.all().order_by('-created')

    bondFilter: BondFilter = BondFilter(
        request.GET, queryset=queryset)
    queryset = bondFilter.qs

    if request.method == constants.POST_METHOD:
        fields: list[str] = [
            'reference_number',
            'bond_type',
            'receiving_method',
            'receiver_name',
            'receiver_account_number',
            'sender_name',
            'sender_account_number',
            'status',
            'amount',
            'transfer_commission',
            'bond_date',
            'created',
            'bond_description',
        ]
        labels_to_change: dict[str, str] = {
            'reference_number': 'رقم المرجع',
            'bond_type': 'نوع السند',
            'receiving_method': 'نوع المعاملة',
            'receiver_name': 'اسم المستلم',
            'receiver_account_number': 'رقم حساب المستلم',
            'sender_name': 'اسم المرسل',
            'sender_account_number': 'رقم حساب المرسل',
            'status': 'الحالة',
            'amount': 'المبلغ',
            'transfer_commission': 'عمولة التحويل',
            'bond_date': 'تاريخ السند',
            'created': 'تاريخ الرفع',
            'bond_description': 'الوصف',
        }
        values_to_change: dict[str, Callable] = {
            'bond_type': lambda bond_type: constants.BOND_TYPE_AR[int(bond_type)],
            'receiving_method': lambda receiving_method: constants.RECEVING_METHOD_AR[int(receiving_method)],
            'status': lambda status: constants.BOND_STATUS_AR[int(status)],
        }
        try:
            file: HttpResponse = exportAsCsvExcel(
                queryset=queryset,
                fields=fields,
                labels_to_change=labels_to_change,
                values_to_change=values_to_change,
                sheet_type=request.POST.get('export_type')
            )
            return file
        except EmptyResultSet:
            MSG.NO_DATA(request)

    page: str = request.GET.get('page')
    pagination = Pagination(queryset, int(page) if page is not None else 1, 3)
    page_obj: QuerySet[Bond] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context: dict[str, Any] = {'bondFilter':bondFilter,
        'page_obj': page_obj, 'is_paginated': is_paginated}
    return render(request, constants.TEMPLATES.BOND_LIST_PAGE_TEMPLATE, context)


def bondDetails(request: HttpRequest, pk: str) -> HttpResponse:
    bond: Bond = get_object_or_404(Bond, pk=pk)
    context: dict[str, Any] = {'bond': bond}
    return render(request, constants.TEMPLATES.BOND_DETAILS_PAGE_TEMPLATE, context)


def authorizeBond(request: HttpRequest, pk: str, reference: str, status: str) -> HttpResponsePermanentRedirect:
    if status == constants.BOND_STATUS.APPROVED or status == constants.BOND_STATUS.CANCELLED or True:
        Bond.objects.filter(id=pk, reference_number=reference).update(status=status)
        # TODO: add activity log and notification message
         
    if 'detail' in request.GET:
        return redirect(constants.PAGES.BOND_DETAILS_PAGE, pk)
    else:
        return redirect(constants.PAGES.ACCOUNTING_PAGE)


def accountListPage(request: HttpRequest) -> HttpResponse:
    queryset: QuerySet[Account] = Account.objects.all().order_by(
        'account_status', '-updated')
    total: float = Account.objects.aggregate(
        total=Sum('balance')).get('total')
    context: dict[str, Any] = {'queryset': queryset, 'total': total}
    return render(request, constants.TEMPLATES.ACCOUNT_LIST_PAGE_TEMPLATE, context)

def addAccountPage(request: HttpRequest) -> HttpResponse:
    accountForm = AccountForm()
    if request.method == constants.POST_METHOD:
        accountForm = AccountForm(request.POST)
        if accountForm.is_valid():
            account: Account = accountForm.save()
            MSG.ADD_ACCOUNT(request)
            logUserActivity(request, constants.ACTION.ADD_BANK_ACCOUNT,
                            f"إضافة حساب بنكي جديد ({account.account_number}) "
                            + f"من قِبل {request.user.get_full_name()}")
            return redirect(constants.PAGES.ACCOUNT_LIST_PAGE)
    
    context: dict[str, Any] = {'accountForm': accountForm}
    return render(request, constants.TEMPLATES.ADD_UPDATE_ACCOUNT_PAGE_TEMPLATE, context)

def updateAccountPage(request: HttpRequest, pk: str) -> HttpResponse:
    account: Account = get_object_or_404(Account, pk=pk)
    accountForm = AccountForm(instance=account)
    if request.method == constants.POST_METHOD:
        accountForm = AccountForm(request.POST, instance=account)
        if accountForm.is_valid():
            account: Account = accountForm.save()
            MSG.UPDATE_ACCOUNT(request)
            logUserActivity(request, constants.ACTION.UPDATE_BANK_ACCOUNT,
                            f" تعديل الحساب البنكي ({account.account_number}) "
                            + f"من قِبل {request.user.get_full_name()}")
            return redirect(constants.PAGES.ACCOUNT_LIST_PAGE)
    
    context: dict[str, Any] = {'accountForm': accountForm}
    return render(request, constants.TEMPLATES.ADD_UPDATE_ACCOUNT_PAGE_TEMPLATE, context)
