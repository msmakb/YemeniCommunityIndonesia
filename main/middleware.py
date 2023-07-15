from datetime import timedelta
import logging
from logging import Logger
import re
import traceback
from typing import Callable

from django.conf import settings
from django.contrib.auth import logout, SESSION_KEY
from django.core.exceptions import (DisallowedHost,
                                    ValidationError,
                                    TooManyFieldsSent,
                                    SuspiciousOperation)
from django.core.cache import cache
from django.db.models import F, Q
from django.http import (HttpResponseBadRequest,
                         HttpResponsePermanentRedirect,
                         HttpResponseForbidden,
                         HttpRequest,
                         HttpResponse,
                         Http404,
                         UnreadablePostError)
from django.shortcuts import redirect, render
from django.urls import reverse, resolve
from django.utils import timezone

from . import constants
from . import messages as MSG
from .models import AuditEntry, BlockedClient
from parameter.service import getParameterValue
from .utils import getClientIp, getUserAgent

logger: Logger = logging.getLogger(constants.LOGGERS.MIDDLEWARE)


class AllowedClientMiddleware(object):

    def __init__(self, get_response) -> None:
        self.get_response: Callable[[HttpRequest], HttpResponse] = get_response
        self.request: HttpRequest = None
        self.requester_ip: str = None
        self.requester_agent: str = None
        self.user: str = None

    def __call__(self, request: HttpRequest) -> HttpResponse | HttpResponsePermanentRedirect | HttpResponseForbidden:
        self.request = request
        self.requester_ip = getClientIp(request)
        self.requester_agent = getUserAgent(request)
        self.user = str(request.user)
        current_path: str = request.path
        current_page_name: str = resolve(request.path_info).url_name

        # Security check
        try:
            request.GET
            request.POST
            request.FILES
        except UnreadablePostError:
            # Do Nothing and Return Bad Request Error
            # This error will occurred when the user stop posting
            # due to the slow internet or any reason
            return HttpResponseBadRequest()
        except TooManyFieldsSent:
            logger.warning("The client is sending many fields with request")
            logger.warning("Get: " + request.GET)
            logger.warning("Post: " + request.POST)
            self.blockClient(indefinitely=True)
            AuditEntry.create(ip=self.requester_ip,
                              user_agent=self.requester_agent,
                              action=constants.ACTION.ATTACK_ATTEMPT,
                              username=self.user)
            return redirect(constants.PAGES.LOGOUT)
        except SuspiciousOperation:
            logger.warning("The client is sending many files with request")
            logger.warning("Files: " + request.FILES)
            self.blockClient(indefinitely=True)
            AuditEntry.create(ip=self.requester_ip,
                              user_agent=self.requester_agent,
                              action=constants.ACTION.ATTACK_ATTEMPT,
                              username=self.user)
            return redirect(constants.PAGES.LOGOUT)

        ip_key = f'IP:{self.requester_ip}'
        if ip_key in cache:
            try:
                request_count = cache.incr(ip_key)
            except ValueError:
                request_count = 1
        else:
            cache.add(ip_key, 1)
            cache.expire(ip_key, 1)
            request_count = 1
        if request_count > getParameterValue(constants.PARAMETERS.REQUEST_MAX_LIMIT_PER_SECOND):
            self.blockClient()

        # Is new visitor
        if self.isNewVisiter():
            AuditEntry.create(ip=self.requester_ip,
                              user_agent=self.requester_agent,
                              action=constants.ACTION.FIRST_VISIT,
                              username=self.user)

        # If the requester posting
        if request.method == constants.POST_METHOD:

            # Donation Limit
            if current_page_name == constants.PAGES.DONATION_PAGE:
                DONATION_LIMIT_CACHE_KEY = 'DONATION:%s' % self.requester_ip
                if cache.has_key(DONATION_LIMIT_CACHE_KEY):
                    donation_count = cache.incr(DONATION_LIMIT_CACHE_KEY)
                else:
                    cache.add(DONATION_LIMIT_CACHE_KEY, 1)
                    cache.expire(DONATION_LIMIT_CACHE_KEY,
                                 constants.DEFAULT_CACHE_EXPIRE)
                    donation_count = 1

                logger.info("DONATION COUNT: %s" % donation_count)
                if donation_count > 5:
                    MSG.DONATION_LIMIT(request)
                    return redirect(constants.PAGES.DONATION_PAGE)

            # Member Form Limit
            if current_page_name == constants.PAGES.MEMBER_FORM_PAGE:
                MEMBER_POST_COUNT_CACHED_KEY: str = "MEMBER_FORM:%s" % self.requester_ip
                membership_form_posts_count: int | None = cache.get(
                    MEMBER_POST_COUNT_CACHED_KEY)

                if not membership_form_posts_count:
                    membership_form_posts_count = 0

                membership_post_limit: int = getParameterValue(
                    constants.PARAMETERS.MEMBER_FORM_POST_LIMIT)
                if membership_form_posts_count >= membership_post_limit:
                    MSG.MEMBERSHIP_FORM_POST_LIMIT(request)
                    return redirect(current_path)

            # Is posting an HTML for attack
            if self.isThereHtmlInPost():
                self.blockClient(indefinitely=True)
                return redirect(constants.PAGES.LOGOUT)

            POST_REQUEST_COUNT: str = "POST:%s" % self.requester_ip
            last_posts_count: int = cache.get(POST_REQUEST_COUNT)

            if last_posts_count:
                last_posts_count += 1
            else:
                last_posts_count = 1

            cache.set(POST_REQUEST_COUNT, last_posts_count, getParameterValue(
                constants.PARAMETERS.BETWEEN_POST_REQUESTS_TIME) / 1000)

            # If the requester spams 2 posts
            if 1 < last_posts_count <= 3:
                MSG.BLOCK_WARNING(request)
                logger.warning(
                    f"The system cut suspicious post requests from "
                    + f"username: {self.user}, IP: {self.requester_ip}")
                return redirect(constants.PAGES.LOGOUT)

            # If the requester spams 3-5 posts
            elif 3 < last_posts_count <= 5:
                self.blockClient()
                AuditEntry.create(ip=self.requester_ip,
                                  user_agent=self.requester_agent,
                                  action=constants.ACTION.SUSPICIOUS_POST,
                                  username=self.user)
                logger.warning(
                    f"The system cut suspicious post requests from "
                    + f"username: {self.user}, IP: {self.requester_ip}")
                return redirect(current_path)

            # If the requester spam more than 5 posts
            elif last_posts_count > 5:
                self.blockClient(indefinitely=True)
                AuditEntry.create(ip=self.requester_ip,
                                  user_agent=self.requester_agent,
                                  action=constants.ACTION.SUSPICIOUS_POST,
                                  username=self.user)
                logger.warning(
                    f"The system cut suspicious post requests from "
                    + f"username: {self.user}, IP: {self.requester_ip}")
                return redirect(current_path)

        # ------------------------------------------------------------------- #
        #       Up this point executed before the response have been set      #
        # ------------------------------------------------------------------- #
        response: HttpResponse = self.get_response(request)                   #
        # ------------------------------------------------------------------- #
        #     After this point everything executed with response been set     #
        # ------------------------------------------------------------------- #

        # If not blocked requester, check the action
        if not self.isBlockedClient():
            # Failed Login Limit
            available_attempts: int = getParameterValue(
                constants.PARAMETERS.ALLOWED_LOGGED_IN_ATTEMPTS)
            CLIENT_FAILED_LOGIN_ATTEMPT_CACHE_KEY: str = "FAIL_LOGIN:%s" % self.requester_ip
            failed_login_attempts: int | None = cache.get(
                CLIENT_FAILED_LOGIN_ATTEMPT_CACHE_KEY)
            if failed_login_attempts:
                available_attempts -= failed_login_attempts

            if not available_attempts:
                logger.warning(
                    f"The user {self.user} does not have any available attempts")
                self.blockClient()
                return redirect(current_path)

        # Check if the temporary block of the requester ended
        elif self.isAllowedToUnblocked():
            blocked_client: BlockedClient = BlockedClient.get(
                ip=self.requester_ip)
            blocked_client.setBlockType(constants.BLOCK_TYPES.UNBLOCKED)
            logger.warning(f"Client at IP address [{self.requester_ip}]"
                           + " was UNBLOCKED!!")
            return redirect(current_path)

        # If blocked requester, send HttpResponseForbidden
        else:
            logger.warning(
                "Blocked Client attempts to get to the site. IP: %s" % self.requester_ip)
            return HttpResponseForbidden(f'<center><h1 style="margin-top: 50px;">لقد تم حظرك من هذا الموقع</h1></center>')
        return response

    def blockClient(self, indefinitely: bool = False) -> None:
        block_type: str = constants.BLOCK_TYPES.TEMPORARY
        if BlockedClient.isExists(ip=self.requester_ip):
            blocked_client: BlockedClient = BlockedClient.get(
                ip=self.requester_ip)
            blocked_times: int = blocked_client.blocked_times
            conditions = (
                indefinitely,
                not (blocked_times < getParameterValue(
                    constants.PARAMETERS.MAX_TEMPORARY_BLOCK) - 1)
            )
            if any(conditions):
                block_type = constants.BLOCK_TYPES.INDEFINITELY
            temp_val: int = 1 if blocked_client.block_type != getParameterValue(
                constants.PARAMETERS.MAX_TEMPORARY_BLOCK) else 0
            blocked_client.setBlockedTimes(blocked_times + temp_val)
            blocked_client.setBlockType(block_type)
        else:
            if indefinitely:
                block_type = constants.BLOCK_TYPES.INDEFINITELY
            BlockedClient.create(ip=self.requester_ip,
                                 user_agent=self.requester_agent,
                                 block_type=block_type
                                 )
        BLACKLISTED_KEY: str = "BLACKLISTED:%s" % self.requester_ip
        WHITELISTED_KEY: str = "WHITELISTED:%s" % self.requester_ip
        cache.delete(WHITELISTED_KEY)
        cache.set(BLACKLISTED_KEY, block_type, None)
        logger.warning(f"Client at IP address [{self.requester_ip}] "
                       + f"was {block_type} blocked")

    def isAllowedToUnblocked(self) -> bool:
        if BlockedClient.objects.annotate(
                time_to_unblocked=F('updated') + timedelta(
                    days=getParameterValue(
                        constants.PARAMETERS.TEMPORARY_BLOCK_PERIOD))
            ).filter(
                ip=self.requester_ip,
                block_type=constants.BLOCK_TYPES.TEMPORARY,
                time_to_unblocked__lte=timezone.now()
        ).exists():
            cache.delete("BLACKLISTED:%s" % self.requester_ip)
            return True

        return False

    def isBlockedClient(self) -> bool:
        BLACKLISTED_KEY: str = "BLACKLISTED:%s" % self.requester_ip
        WHITELISTED_KEY: str = "WHITELISTED:%s" % self.requester_ip

        if not cache.has_key(BLACKLISTED_KEY) and cache.has_key(WHITELISTED_KEY):
            return False

        if BlockedClient.objects.filter(
            ~Q(block_type=constants.BLOCK_TYPES.UNBLOCKED),
            ip=self.requester_ip,
        ).exists():
            cache.set(BLACKLISTED_KEY, None, None)
            return True

        cache.set(WHITELISTED_KEY, None, constants.DEFAULT_CACHE_EXPIRE)
        return False

    def isNewVisiter(self) -> bool:
        # Check first in the last audit entry, if not: check for all
        VISITOR_KEY: str = "VST:%s" % self.requester_ip
        if cache.has_key(VISITOR_KEY):
            return False

        cache.set(VISITOR_KEY, None, constants.DEFAULT_CACHE_EXPIRE)
        if any((
            AuditEntry.filter(
                id__gte=getParameterValue(
                constants.PARAMETERS.MAGIC_NUMBER),
                ip=self.requester_ip).exists(),
            AuditEntry.isExists(ip=self.requester_ip)
        )):
            return False
        else:
            return True

    def isThereHtmlInPost(self) -> bool:
        pattern: re.Pattern[str] = re.compile(constants.HTML_TAGS_PATTERN)
        for values in self.request.POST.values():
            if re.search(pattern, values):
                AuditEntry.create(ip=self.requester_ip,
                                  user_agent=self.requester_agent,
                                  action=constants.ACTION.ATTACK_ATTEMPT,
                                  username=self.user)
                logger.warning(
                    "Attacking attempt detected. Attacker information "
                    + f"IP: {self.requester_ip} Username: {self.request.user} "
                    + f"User Agent: {self.requester_agent}")
                logger.warning("Post: " + self.request.POST)
                return True
        return False


class LoginRequiredMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response: Callable[[HttpRequest], HttpResponse] = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response: HttpResponse = self.get_response(request)

        return response

    def process_view(self, request: HttpRequest, *args, **kwargs) -> HttpResponsePermanentRedirect | None:
        time_out: int = getParameterValue(constants.PARAMETERS.TIME_OUT_PERIOD)
        if not request.user.is_authenticated:
            if request.path.startswith(reverse('admin:index')):
                logger.warning(f'Non-allowed user [{request.user}] attempted '
                               + f'to access admin site at "{request.get_full_path()}".'
                               + f' IP: {getClientIp(request)}')
                raise Http404
            path: str = resolve(request.path_info).url_name
            if path in constants.RESTRICTED_PAGES:
                return redirect(constants.PAGES.UNAUTHORIZED_PAGE)
            else:
                return None
        elif request.user.last_login < timezone.now() - timedelta(minutes=time_out):
            CACHED_USER_KEY = "USER:" + request.session[SESSION_KEY]
            cache.delete(CACHED_USER_KEY)
            MSG.TIME_OUT(request)
            logout(request)
            return redirect(constants.PAGES.INDEX_PAGE)
        return None


class SiteUnderMaintenanceMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response: Callable[[HttpRequest], HttpResponse] = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if settings.UNDER_MAINTENANCE:
            if request.user.is_authenticated:
                logout(request)
            return render(request, constants.TEMPLATES.UNDER_MAINTENANCE_PAGE_TEMPLATE)

        response: HttpResponse = self.get_response(request)

        return response


class ErrorHandlerMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response: Callable[[HttpRequest], HttpResponse] = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:

        response: HttpResponse = self.get_response(request)

        return response

    def process_exception(self, request: HttpRequest, exception: Exception) -> HttpResponse:
        if settings.DEBUG:
            return

        if isinstance(exception, ValidationError):
            return None
        if isinstance(exception, DisallowedHost):
            return None
        if isinstance(exception, Http404):
            return None

        if cache.get('ERROR_' + getClientIp(request)) == type(exception):
            cache.delete('ERROR_' + getClientIp(request))
            if request.user.is_authenticated:
                logout(request)
            return redirect(constants.PAGES.INDEX_PAGE)

        MSG.SOMETHING_WRONG(request)
        logger.error(traceback.format_exc())
        if request.user.is_authenticated and request.user.is_staff:
            MSG.ERROR_MESSAGE(request, exception)
            MSG.SCREENSHOT(request)

        cache.set('ERROR_' + getClientIp(request), type(exception), timeout=5)
        return redirect(request.path)
