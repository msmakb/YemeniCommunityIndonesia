import logging
from logging import Logger

from django.contrib.auth import get_user, SESSION_KEY
from django.core.cache import cache
from django.http import (HttpResponsePermanentRedirect,
                         HttpResponseForbidden,
                         HttpRequest,
                         Http404)
from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.utils.deprecation import MiddlewareMixin

from main import constants
from main import messages as MSG
from main.utils import getClientIp
from member.models import Person

from .models import CompanyUser

logger: Logger = logging.getLogger(constants.LOGGERS.MIDDLEWARE)


class AllowedUserMiddleware(MiddlewareMixin):

    def process_request(self, request: HttpRequest, *args, **kwargs) -> HttpResponsePermanentRedirect | None:

        # Media allowed for staff only exclude the public dir
        if '/media/' in request.path and '/public/' not in request.path and (not request.user.is_authenticated or not request.user.is_staff):
            return HttpResponseForbidden("Access Denied")

        if request.user.is_authenticated:
            requested_page: str = resolve(request.path_info).url_name
            if not self.isAllowedToAccessAdmin(request):
                raise Http404

            if requested_page == constants.PAGES.UNAUTHORIZED_PAGE:
                return None

            if request.user.is_superuser:
                if requested_page in constants.NON_STAFF_RESTRICTED_PAGES and requested_page not in constants.STAFF_RESTRICTED_PAGES:
                    return redirect(constants.PAGES.INDEX_PAGE)
                return None

            if request.user.is_staff:
                if requested_page in constants.STAFF_PERMISSIONS["COMMON"]:
                    return None

                try:
                    company_user: CompanyUser = CompanyUser.getCompanyUserByUserObject(
                        request.user)
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
                if requested_page not in constants.RESTRICTED_PAGES:
                    return None

                if requested_page in constants.NON_STAFF_PERMISSIONS["COMMON"]:
                    return None

                user_data = Person.getUserData(request.user)
                has_membership: bool = user_data.get('has_membership')

                if requested_page in constants.NON_STAFF_PERMISSIONS['WITH_MEMBERSHIP_ONLY'] and has_membership:
                    return None

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


class CacheUserMiddleware(MiddlewareMixin):

    def process_request(self, request) -> HttpRequest:
        if not hasattr(request, 'session') or not request.session.get(SESSION_KEY):
            return

        CACHED_USER_KEY = "USER:%s" % request.session[SESSION_KEY]
        request._cached_user = cache.get(CACHED_USER_KEY)
        if request._cached_user:
            cache.touch(CACHED_USER_KEY)
            return

        request._cached_user = get_user(request)
        cache.set(CACHED_USER_KEY, request._cached_user, 300)
