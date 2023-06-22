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
        'Payment/List/',
        views.membershipPaymentListPage,
        name=PAGES.MEMBERSHIP_PAYMENT_LIST_PAGE
    ),
    path(
        'Payment/Pending/',
        views.membershipPaymentPendingListPage,
        name=PAGES.MEMBERSHIP_PAYMENT_PENDING_LIST_PAGE
    ),
    path(
        'Payment/Api/Period/<str:pk>/<str:number_of_months>/',
        views.getPaymentPeriod,
        name=PAGES.GET_PAYMENT_PERIOD_API
    ),
]
