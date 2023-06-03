from django.urls import path

from main.constants import PAGES

from . import views

urlpatterns = [
    path(
        'User-Management/',
        views.usersPage,
        name=PAGES.COMPANY_USERS_PAGE
    ),
    path(
        'User-Management/Add/',
        views.addUserPage,
        name=PAGES.ADD_COMPANY_USER_PAGE
    ),
    path(
        'User-Management/Update/<str:pk>/',
        views.updateUserPage,
        name=PAGES.UPDATE_COMPANY_USER_PAGE
    ),
    path(
        'User-Management/Delete/<str:pk>/',
        views.deleteUserPage,
        name=PAGES.DELETE_COMPANY_USER_PAGE
    ),
    path(
        'User-Management/Roles/',
        views.rolesPage,
        name=PAGES.ROLES_PAGE
    ),
    path(
        'User-Management/Roles/Add/',
        views.addRolePage,
        name=PAGES.ADD_ROLE_PAGE
    ),
    path(
        'User-Management/Roles/Update/<str:pk>/',
        views.updateRolePage,
        name=PAGES.UPDATE_ROLE_PAGE
    ),
    path(
        'User-Management/Roles/Delete/<str:pk>/',
        views.deleteRolePage,
        name=PAGES.DELETE_ROLE_PAGE
    ),
    path(
        'User-Registration/<str:uid_b64>/<str:token>/',
        views.newCompanyUserRegistrationPage,
        name=PAGES.COMPANY_USER_REGISTRATION_PAGE
    ),
]
