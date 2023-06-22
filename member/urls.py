from django.urls import path
from . import views
from main.constants import PAGES

urlpatterns = [
    path(
        'Staff-Dashboard/',
        views.staffDashboard,
        name=PAGES.STAFF_DASHBOARD
    ),
    path(
        'Members/<str:currentPage>/',
        views.membersPage,
        name=PAGES.MEMBERS_PAGE
    ),
    path(
        'Members/Detail-Member/<str:pk>',
        views.detailMember,
        name=PAGES.DETAIL_MEMBER_PAGE
    ),
    path(
        'Member-Dashboard/',
        views.memberPage,
        name=PAGES.MEMBER_DASHBOARD
    ),
    path(
        'Membership-Card/',
        views.membershipCardPage,
        name=PAGES.MEMBERSHIP_CARD_PAGE
    ),
    path(
        'Membership-Card/Download/',
        views.downloadMembershipCard,
        name=PAGES.DOWNLOAD_MEMBERSHIP_PAGE
    ),
    path(
        'MemberForm/',
        views.memberFormPage,
        name=PAGES.MEMBER_FORM_PAGE
    ),
    path(
        'Thank-You/',
        views.thankYou,
        name=PAGES.THANK_YOU_PAGE
    ),
]
