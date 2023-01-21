from django.urls import path
from . import views
from main.constants import PAGES

urlpatterns = [
    path(
        'Manager/Dashboard/<str:currentPage>/',
        views.dashboard,
        name=PAGES.DASHBOARD
    ),
    path(
        'Manager/Detail-Member/<str:pk>',
        views.detailMember,
        name=PAGES.DETAIL_MEMBER_PAGE
    ),
    path(
        'Member/',
        views.memberPage,
        name=PAGES.MEMBER_PAGE
    ),
    path(
        'Member/Membership-Card/<str:pk>',
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
