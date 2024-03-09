from django.urls import path
from . import views

from main.constants import PAGES

urlpatterns = [
    path(
        'Membership-Payment/',
        views.membershipPaymentPage,
        name=PAGES.MEMBERSHIP_PAYMENT_PAGE
    ),
    path(
        'Payment-History/',
        views.membershipPaymentHistoryPage,
        name=PAGES.MEMBERSHIP_PAYMENT_HISTORY_PAGE
    ),
    path(
        'Payment/Receipt/<str:reference_number>/',
        views.getReceipt,
        name=PAGES.MEMBERSHIP_PAYMENT_RECEIPT
    ),
    path(
        'Accounting/Payment/List/',
        views.membershipPaymentListPage,
        name=PAGES.MEMBERSHIP_PAYMENT_LIST_PAGE
    ),
    path(
        'Accounting/Payment/Pending/',
        views.membershipPaymentPendingListPage,
        name=PAGES.MEMBERSHIP_PAYMENT_PENDING_LIST_PAGE
    ),
    path(
        'Accounting/Payment/Add/',
        views.addMembershipPaymentsPage,
        name=PAGES.ADD_MEMBERSHIP_PAYMENTS_PAGE
    ),
    path(
        'Payment/Api/Period/<str:pk>/<str:number_of_months>/',
        views.getPaymentPeriod,
        name=PAGES.GET_PAYMENT_PERIOD_API
    ),
]
