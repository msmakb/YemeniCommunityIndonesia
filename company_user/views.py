from typing import Any

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db.transaction import atomic
from django.db.models.deletion import ProtectedError
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, Http404, QueryDict
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from main import constants
from main import messages as MSG
from main.utils import Pagination, generateRandomString, logUserActivity, account_activation_token

from .models import CompanyUser, Role
from .forms import ChangeUserDataForm, RoleForm, CreateUserForm, SetUsernameAndPasswordForm


def usersPage(request: HttpRequest) -> HttpResponse:
    queryset: QuerySet[CompanyUser] = CompanyUser.getAllOrdered(
        'user__first_name').select_related('user')
    page: str = request.GET.get('page')
    pagination = Pagination(queryset, int(page) if page is not None else 1,
                            paginate_by=15)
    page_obj: QuerySet[CompanyUser] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context: dict[str, Any] = {'page_obj': page_obj,
                               'is_paginated': is_paginated}
    return render(request, constants.TEMPLATES.COMPANY_USERS_PAGE_TEMPLATE, context)


def rolesPage(request: HttpRequest) -> HttpResponse:
    queryset: QuerySet[Role] = Role.getAllOrdered(
        'name').exclude(name='superuser').prefetch_related('groups')
    page: str = request.GET.get('page')
    pagination = Pagination(queryset, int(page) if page is not None else 1,
                            paginate_by=15)
    page_obj: QuerySet[Role] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context: dict[str, Any] = {'page_obj': page_obj,
                               'is_paginated': is_paginated}
    return render(request, constants.TEMPLATES.ROLES_PAGE_TEMPLATE, context)


def addUserPage(request: HttpRequest) -> HttpResponse:
    user_form: CreateUserForm = CreateUserForm(request.user.is_superuser)

    if request.method == constants.POST_METHOD:
        updated_post: QueryDict = request.POST.copy()
        password: str = generateRandomString()
        updated_post.update(
            {
                'username': generateRandomString(),
                'password1': password,
                'password2': password,
                'is_staff': True,
            }
        )
        user_form: CreateUserForm = CreateUserForm(
            request.user.is_superuser, updated_post)
        if user_form.is_valid():
            role_id: int = int(updated_post.get('role'))
            user: User = user_form.save(commit=False)
            user.is_active = False
            if role_id == 0:
                user.is_superuser = True
                if not request.user.is_superuser:
                    MSG.SOMETHING_WRONG(request)
                    return redirect(constants.PAGES.LOGOUT)

            with atomic():
                # If fails to send the activation like via email,
                # no need to save the user to database. The atomic
                # function will be rolled back, and none of the
                # changes made within the transaction will be
                # persisted in the database.
                user.save()
                if user.is_superuser:
                    CompanyUser.create(role=Role.get(
                        name='superuser'), user=user)
                else:
                    CompanyUser.create(role=Role.get(
                        id=role_id), user=user)

                message: str = render_to_string(
                    constants.TEMPLATES.NEW_COMPANY_USER_EMAIL_TEMPLATE,
                    {
                        'user': user,
                        'domain': get_current_site(request).domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': account_activation_token.make_token(user),
                        "protocol": 'https' if request.is_secure() else 'http'
                    }
                )
                email: EmailMessage = EmailMessage(
                    subject="مرحبًا بك في منصتنا! قم بتفعيل حسابك",
                    body=message,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[user.email]
                )
                email.send()

            logUserActivity(request, constants.ACTION.ADD_USER,
                            f"إضافة مستخدم جديد ({user.get_full_name()}) "
                            + f"من قِبل {request.user.get_full_name()}")
            MSG.ADD_USER(request)
            return redirect(constants.PAGES.COMPANY_USERS_PAGE)

    context: dict[str, Any] = {'userForm': user_form}
    return render(request, constants.TEMPLATES.ADD_UPDATE_COMPANY_USER_PAGE_TEMPLATE, context)


def updateUserPage(request: HttpRequest, pk: str) -> HttpResponse:
    user: User = get_object_or_404(User, pk=pk)
    user_form: ChangeUserDataForm = ChangeUserDataForm(instance=user)

    if user.username == 'admin' and request.user.username != 'admin':
        raise Http404

    if request.method == constants.POST_METHOD:
        user_form: ChangeUserDataForm = ChangeUserDataForm(
            request.POST, instance=user)
        if user_form.is_valid():
            role_id: int = int(request.POST.get('role'))
            user: User = user_form.save(commit=False)

            if role_id == 0:
                user.is_superuser = True
                if not request.user.is_superuser:
                    MSG.SOMETHING_WRONG(request)
                    return redirect(constants.PAGES.LOGOUT)
            else:
                user.is_superuser = False

            user.save()
            if user.is_superuser:
                CompanyUser.filter(user=user).update(role=Role.get(
                    name='superuser'))
            else:
                CompanyUser.filter(user=user).update(role=Role.get(
                    id=role_id))

            logUserActivity(request, constants.ACTION.UPDATE_USER,
                            f"تعديل بيانات المستخدم ({user.get_full_name()}) "
                            + f"من قِبل {request.user.get_full_name()}")
            MSG.UPDATE_USER(request)
            return redirect(constants.PAGES.COMPANY_USERS_PAGE)

    context: dict[str, Any] = {'userForm': user_form}
    return render(request, constants.TEMPLATES.ADD_UPDATE_COMPANY_USER_PAGE_TEMPLATE, context)


def deleteUserPage(request: HttpRequest, pk: str) -> HttpResponse:
    user: User = get_object_or_404(User, pk=pk)
    if not user.is_staff or user.username == 'admin':
        raise Http404

    user.delete()
    logUserActivity(request, constants.ACTION.DELETE_USER,
                    f"حذف المستخدم ({user.get_full_name()}) "
                    + f"من قِبل {request.user.get_full_name()}")
    MSG.DELETE_USER(request)
    return redirect(constants.PAGES.COMPANY_USERS_PAGE)


def addRolePage(request: HttpRequest) -> HttpResponse:
    role_form: RoleForm = RoleForm(request.user.is_superuser)

    if request.method == constants.POST_METHOD:
        role_form: RoleForm = RoleForm(request.user.is_superuser, request.POST)
        if role_form.is_valid():
            role: Role = role_form.save()
            logUserActivity(request, constants.ACTION.ADD_ROLE,
                            f"إضافة وظيفة جديدة ({role.name}) "
                            + f"من قِبل {request.user.get_full_name()}")

            MSG.ADD_ROLE(request)
            return redirect(constants.PAGES.ROLES_PAGE)

    context: dict[str, Any] = {'roleForm': role_form,
                               'groupsAr': constants.GROUPS_AR}
    return render(request, constants.TEMPLATES.ADD_UPDATE_ROLE_PAGE_TEMPLATE, context)


def updateRolePage(request: HttpRequest, pk: str) -> HttpResponse:
    role: Role = get_object_or_404(Role, pk=pk)
    role_form: RoleForm = RoleForm(request.user.is_superuser, instance=role)

    if request.method == constants.POST_METHOD:
        role_form: RoleForm = RoleForm(
            request.user.is_superuser, request.POST, instance=role)
        if role_form.is_valid():
            role_form.save()
            logUserActivity(request, constants.ACTION.UPDATE_ROLE,
                            f"تعديل الوظيفة ({role.name}) "
                            + f"من قِبل {request.user.get_full_name()}")

            MSG.UPDATE_ROLE(request)
            return redirect(constants.PAGES.ROLES_PAGE)

    context: dict[str, Any] = {'roleForm': role_form,
                               'groupsAr': constants.GROUPS_AR}
    return render(request, constants.TEMPLATES.ADD_UPDATE_ROLE_PAGE_TEMPLATE, context)


def deleteRolePage(request: HttpRequest, pk: str) -> HttpResponse:
    try:
        role: Role = get_object_or_404(Role, pk=pk)
        role.delete()
        logUserActivity(request, constants.ACTION.DELETE_ROLE,
                        f"حذف الوظيفة ({role.name}) "
                        + f"من قِبل {request.user.get_full_name()}")
    except ProtectedError:
        MSG.PROTECTED_ROLE(request)
        return redirect(constants.PAGES.ROLES_PAGE)

    MSG.DELETE_ROLE(request)
    return redirect(constants.PAGES.ROLES_PAGE)


def newCompanyUserRegistrationPage(request: HttpRequest, uid_b64: str, token: str) -> HttpResponse:
    if request.user.is_authenticated:
        auth.logout(request)

    try:
        uid: str = force_str(urlsafe_base64_decode(uid_b64))
        user: User = get_object_or_404(User, pk=uid)
    except Exception as _:
        raise Http404

    if user.is_active:
        raise Http404

    if user.date_joined + timezone.timedelta(hours=1) < timezone.now():
        user.delete()
        raise Http404

    if not account_activation_token.check_token(user, token):
        user.delete()
        raise Http404

    form = SetUsernameAndPasswordForm(user)
    if request.method == constants.POST_METHOD:
        form = SetUsernameAndPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            MSG.USER_REGISTRATION_DONE(request)
            logUserActivity(request, constants.ACTION.COMPLETE_USER_REGISTRATION,
                            f"استكمال تسجيل المستخدم ({user.get_full_name()})")
            return redirect(constants.PAGES.INDEX_PAGE)

    context: dict[str, Any] = {'form': form}
    return render(request, constants.TEMPLATES.COMPANY_USER_REGISTRATION_PAGE_TEMPLATE, context)
