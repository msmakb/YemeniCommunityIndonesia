from django.urls import path
from . import views

from main.constants import PAGES

urlpatterns = [
    path(
        'Accounting/',
        views.accountingPage,
        name=PAGES.ACCOUNTING_PAGE
    ),
    path(
        'Accounting/Bond/Bond-List/',
        views.bondListPage,
        name=PAGES.BOND_LIST_PAGE
    ),
    path(
        'Accounting/Bond/<str:pk>/',
        views.bondDetails,
        name=PAGES.BOND_DETAILS_PAGE
    ),
    path(
        'Accounting/Accounts/',
        views.accountListPage,
        name=PAGES.ACCOUNT_LIST_PAGE
    ),
    path(
        'Accounting/Accounts/Add/',
        views.addAccountPage,
        name=PAGES.ADD_ACCOUNT_PAGE
    ),
    path(
        'Accounting/Accounts/Update/<str:pk>/',
        views.updateAccountPage,
        name=PAGES.UPDATE_ACCOUNT_PAGE
    ),
    path(
        'Accounting/Authorize-Bond/<str:pk>/<str:reference>/<str:status>/',
        views.authorizeBond,
        name=PAGES.AUTHORIZE_BOND
    ),
]
