from datetime import timedelta
import logging
from logging import Logger
import re
from typing import Callable

from django.contrib.auth import logout
from django.db.models.query import QuerySet
from django.http import (HttpResponsePermanentRedirect,
                         HttpResponseForbidden,
                         HttpRequest,
                         HttpResponse,
                         Http404)
from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.utils import timezone
from django.utils.timezone import datetime

from . import constants
from . import messages as MSG
from .models import AuditEntry, BlockedClient
from .parameters import getParameterValue
from .utils import getClientIp, getUserAgent, getUserGroupe

logger: Logger = logging.getLogger(constants.LOGGERS.MIDDLEWARE)


class AllowedClientMiddleware(object):

    def __init__(self, get_response) -> None:
        self.get_response: Callable[[HttpRequest], HttpResponse] = get_response
        self.request: HttpRequest = None
        self.requester_ip: str = None
        self.requester_agent: str = None
        self.user: str = None
        self.last_audit_entry: QuerySet[AuditEntry] = None

    def __call__(self, request: HttpRequest) -> HttpResponse | HttpResponsePermanentRedirect | HttpResponseForbidden:
        self.request = request
        self.requester_ip = getClientIp(request)
        self.requester_agent = getUserAgent(request)
        self.user = str(request.user)
        # ------------------------------------------------------------- #
        # This is the last object that is not included of the specified #
        # period of allowed logged in attempts reset                    #
        # Ex. if the parameter 'ALLOWED_LOGGED_IN_ATTEMPTS_RESET'       #
        # set to 7 days, the last object that will be reset, It will be #
        # saved in the in 'MAGIC_NUMBER' parameter, to make the search  #
        # in the table 'AuditEntry' faster and more scalable            #
        start_chunk_object_id: int = getParameterValue(                 #
            constants.PARAMETERS.MAGIC_NUMBER)                          #
        self.last_audit_entry = AuditEntry.filter(                      #
            id__gte=start_chunk_object_id)                              #
        # ------------------------------------------------------------- #
        current_path = request.path

        # Is new visitor
        if self.isNewVisiter():
            AuditEntry.create(ip=self.requester_ip,
                              user_agent=self.requester_agent,
                              action=constants.ACTION.FIRST_VISIT,
                              username=self.user)

        # If the requester posting
        if request.method == constants.POST_METHOD:

            # Is posting an HTML for attack
            if self.isThereHtmlInPost():
                self.blockClient(indefinitely=True)
                return redirect(constants.PAGES.LOGOUT)

            # Create normal post to save the client last post request
            AuditEntry.create(ip=self.requester_ip,
                              user_agent=self.requester_agent,
                              action=constants.ACTION.NORMAL_POST,
                              username=self.user)

            time: datetime = timezone.now() - timedelta(
                milliseconds=getParameterValue(
                    constants.PARAMETERS.BETWEEN_POST_REQUESTS_TIME))

            membership_form_posts_count: int = self.last_audit_entry.filter(
                ip=self.requester_ip,
                action=constants.ACTION.MEMBER_FORM_POST).count()

            membership_post_limit: int = getParameterValue(
                constants.PARAMETERS.MEMBER_FORM_POST_LIMIT)
            if resolve(request.path_info).url_name == constants.PAGES.MEMBER_FORM_PAGE:
                if membership_form_posts_count >= membership_post_limit:
                    MSG.MEMBERSHIP_FORM_POST_LIMIT(request)
                    return redirect(current_path)

            last_posts_count: int = self.last_audit_entry.filter(
                ip=self.requester_ip,
                action=constants.ACTION.NORMAL_POST,
                created__gte=time).count()

            # If the requester spams 2 posts
            if 1 < last_posts_count <= 3:
                MSG.BLOCK_WARNING(request)
                logger.warning(
                    f"The system cut suspicious post requests from "
                    + f"username: {self.user}, IP: {self.requester_ip}")
                return redirect(constants.PAGES.LOGOUT)

            # If the requester spams 3-5 posts
            elif 3 < last_posts_count <= 5:
                AuditEntry.create(ip=self.requester_ip,
                                  user_agent=self.requester_agent,
                                  action=constants.ACTION.SUSPICIOUS_POST,
                                  username=self.user)
                logger.warning(
                    f"The system cut suspicious post requests from "
                    + f"username: {self.user}, IP: {self.requester_ip}")
                self.blockClient()
                return redirect(current_path)

            # If the requester spam more than 5 posts
            elif last_posts_count > 5:
                self.blockClient(indefinitely=True)
                logger.warning(
                    f"The system cut suspicious post requests from "
                    + f"username: {self.user}, IP: {self.requester_ip}")
                return redirect(current_path)

            # If it's normal post, then cleanup
            else:
                self.cleanupUnsuspiciousPostRequests()

        # ------------------------------------------------------------------- #
        #       Up this point executed before the response have been set      #
        # ------------------------------------------------------------------- #
        response: HttpResponse = self.get_response(request)                   #
        # ------------------------------------------------------------------- #
        #     After this point everything executed with response been set     #
        # ------------------------------------------------------------------- #

        # If not blocked requester, check the action
        if not self.isBlockedClient():
            allowed_logged_in_attempts: int = getParameterValue(
                constants.PARAMETERS.ALLOWED_LOGGED_IN_ATTEMPTS)
            requester_attempts: int = self.getRequesterFailedAttempts()
            available_attempts: int = allowed_logged_in_attempts

            if BlockedClient.isExists(ip=self.requester_ip):
                blocked_client: BlockedClient = BlockedClient.get(
                    ip=self.requester_ip)
                available_attempts = allowed_logged_in_attempts * \
                    (blocked_client.blocked_times + 1)
            count_sus: int = self.last_audit_entry.filter(
                ip=self.requester_ip,
                action=constants.ACTION.SUSPICIOUS_POST).count() * 5
            available_attempts -= requester_attempts
            available_attempts -= count_sus

            if not available_attempts:
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
            blocked_client: BlockedClient = BlockedClient.get(
                ip=self.requester_ip)
            logger.warning("Blocked Client attempts to get to the site.")
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
        logger.warning(f"Client at IP address [{self.requester_ip}] "
                       + f"was {block_type} blocked")

    def cleanupUnsuspiciousPostRequests(self) -> None:
        last_posts: QuerySet[AuditEntry] = self.last_audit_entry.filter(
            ip=self.requester_ip,
            action=constants.ACTION.NORMAL_POST)
        for index, post in enumerate(last_posts):
            if index == last_posts.count() - 1:
                break
            else:
                post.delete()

    def getRequesterFailedAttempts(self) -> int:
        failed_attempts: QuerySet[AuditEntry] = self.last_audit_entry.filter(
            ip=self.requester_ip,
            action=constants.ACTION.LOGGED_FAILED)

        return failed_attempts.count()

    def isAllowedToUnblocked(self) -> bool:
        blocked_client: BlockedClient = BlockedClient.get(ip=self.requester_ip)
        block_type: str = blocked_client.block_type
        if block_type == constants.BLOCK_TYPES.TEMPORARY:
            blocked_time: datetime = blocked_client.updated
            time_to_unblocked: datetime = blocked_time + timedelta(
                days=getParameterValue(
                    constants.PARAMETERS.TEMPORARY_BLOCK_PERIOD))
            if time_to_unblocked <= timezone.now():
                return True
        return False

    def isBlockedClient(self) -> bool:
        if BlockedClient.isExists(ip=self.requester_ip):
            blocked_client: BlockedClient = BlockedClient.get(
                ip=self.requester_ip)
            if blocked_client.block_type is not constants.BLOCK_TYPES.UNBLOCKED:
                return True
        return False

    def isNewVisiter(self) -> bool:
        # Check first in the last audit entry, if not: check for all
        if self.last_audit_entry.filter(ip=self.requester_ip).exists():
            return False
        elif AuditEntry.isExists(ip=self.requester_ip):
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
            MSG.TIME_OUT(request)
            logout(request)
            return redirect(constants.PAGES.INDEX_PAGE)
        return None


class AllowedUserMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response: Callable[[HttpRequest], HttpResponse] = get_response
        self.request: HttpRequest = None

    def __call__(self, request: HttpRequest) -> HttpResponse:
        self.request = request
        response: HttpResponse = self.get_response(request)

        return response

    def process_view(self, request: HttpRequest, *args, **kwargs) -> HttpResponsePermanentRedirect | None:
        if request.user.is_authenticated:
            path_name: str = resolve(request.path_info).url_name
            # Is requesting admin dashboard
            if not self.isAllowedToAccessAdmin(request):
                raise Http404

            # The requester in THE unauthorized page
            elif path_name == constants.PAGES.UNAUTHORIZED_PAGE:
                return None
            elif request.user.groups.exists():
                group: str = getUserGroupe(request)
                if path_name in constants.RESTRICTED_PAGES and path_name not in constants.PERMISSIONS[group]:
                    return redirect(constants.PAGES.UNAUTHORIZED_PAGE)
            else:
                MSG.SOMETHING_WRONG(request)
                logger.warning(f"The user [{request.user}] has no groups!!")
                return redirect(constants.PAGES.LOGOUT)

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
