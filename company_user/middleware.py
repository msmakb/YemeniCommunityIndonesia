import logging
from logging import Logger
from typing import Callable

from django.contrib.auth import logout
from django.http import (HttpResponsePermanentRedirect,
                         HttpResponseForbidden,
                         HttpRequest,
                         HttpResponse,
                         Http404)
from django.shortcuts import redirect
from django.urls import reverse, resolve
from company_user.models import CompanyUser

from main import constants
from main import messages as MSG
from main.utils import getClientIp, getUserGroupe

logger: Logger = logging.getLogger(constants.LOGGERS.MIDDLEWARE)


class AllowedUserMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response: Callable[[HttpRequest], HttpResponse] = get_response
        self.request: HttpRequest = None

    def __call__(self, request: HttpRequest) -> HttpResponse:
        self.request = request
        response: HttpResponse = self.get_response(request)
        # Media allowed for staff only
        if request.path.startswith('/media/') and (not request.user.is_authenticated or not request.user.is_staff):
            return HttpResponseForbidden()

        return response

    def process_view(self, request: HttpRequest, *args, **kwargs) -> HttpResponsePermanentRedirect | None:
        if request.user.is_authenticated:
            requested_page: str = resolve(request.path_info).url_name
            if not self.isAllowedToAccessAdmin(request):
                raise Http404

            if requested_page == constants.PAGES.UNAUTHORIZED_PAGE:
                return None

            if request.user.is_superuser:
                return None

            if request.user.is_staff:
                if requested_page in constants.STAFF_PERMISSIONS["COMMON"]:
                    return None

                try:
                    company_user: CompanyUser = CompanyUser.get(
                        user=request.user)
                    if requested_page in constants.RESTRICTED_PAGES and requested_page not in company_user.role.permissions:
                        logger.warning(
                            f'The company user {company_user} tried to access non allowed page for this user.')
                        return redirect(constants.PAGES.UNAUTHORIZED_PAGE)
                except CompanyUser.DoesNotExist:
                    MSG.SOMETHING_WRONG(request)
                    logger.warning(
                        f"The staff user [{request.user}] has no company user!!")
                    return redirect(constants.PAGES.LOGOUT)
            else:
                if requested_page in constants.RESTRICTED_PAGES and requested_page not in constants.NON_STAFF_PERMISSIONS:
                    return redirect(constants.PAGES.UNAUTHORIZED_PAGE)
        return None

    def isAllowedToAccessAdmin(self, request: HttpRequest) -> bool:
        if request.path.startswith(reverse('admin:index')):
            if request.user.is_superuser:
                return True
            else:
                logger.warning(f'Non-allowed user [{request.user}] attempted '
                               + f'to access admin site at "{request.get_full_path()}".'
                               + f' IP: {getClientIp(request)}')
                return False
        return True
