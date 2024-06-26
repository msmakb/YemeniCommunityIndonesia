from django.urls import path
from . import views
from .constants import PAGES

urlpatterns = [
    path(
        '',
        views.index,
        name=PAGES.INDEX_PAGE
    ),
    path(
        'Login/',
        views.loginPage,
        name=PAGES.LOGIN_PAGE
    ),
    path(
        'Error/',
        views.unauthorized,
        name=PAGES.UNAUTHORIZED_PAGE
    ),
    path(
        'MembershipTerms/',
        views.membershipTerms,
        name=PAGES.MEMBERSHIP_TERMS_PAGE
    ),
    path(
        'About/',
        views.about,
        name=PAGES.ABOUT_PAGE
    ),
    path(
        'Logout/',
        views.logoutUser,
        name=PAGES.LOGOUT
    ),
    path(
        'Donation/',
        views.donation,
        name=PAGES.DONATION_PAGE
    ),
    path(
        'Donation/Thank-You/',
        views.thanksForDonation,
        name=PAGES.THANKS_FOR_DONATION_PAGE
    ),
    path(
        'Accounting/Donation-List/',
        views.donationListPage,
        name=PAGES.DONATION_LIST_PAGE
    ),
]
