from django.urls import path
from . import views
from main.constants import PAGES

urlpatterns = [
    path(
        'Manager/Dashboard/',
        views.dashboard,
        name=PAGES.DASHBOARD
    ),
    path(
        'Manager/Detail-Member/<str:pk>',
        views.detailMember,
        name=PAGES.DETAIL_MEMBER_PAGE
    ),
    path(
        'Member/<str:pk>/',
        views.memberPage,
        name=PAGES.MEMBER_PAGE
    ),
    path(
        'MemberForm/',
        views.memberFormPage,
        name=PAGES.MEMBER_FORM_PAGE
    ),
]
