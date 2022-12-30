import logging
from typing import Union

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.http import HttpRequest

from . import constants

logger = logging.getLogger(constants.LOGGERS.MAIN)
logger_models = logging.getLogger(constants.LOGGERS.MODELS)


class Pagination:

    def __init__(self, queryset: QuerySet, page_num: int, paginate_by: int = constants.ROWS_PER_PAGE):
        self.page_num: int = page_num
        self.paginator: Paginator = Paginator(queryset, paginate_by)

    def getPageObject(self) -> QuerySet:
        return self.paginator.get_page(self.page_num)

    @property
    def isPaginated(self) -> bool:
        return True if self.paginator.num_pages > 1 else False


def getUserGroupe(requester: Union[HttpRequest, User]) -> str:
    user: User = None
    if isinstance(requester, User):
        user = requester
    elif isinstance(requester, HttpRequest):
        user = requester.user
    else:
        raise ValueError("Requester must be a User or HttpRequest object.")
    try:
        user_groups = user.groups.all()[0]
        return user_groups.name
    except IndexError:
        return None


def getClientIp(request: HttpRequest) -> str:
    http_x_forwarded_for: str = request.META.get('HTTP_X_FORWARDED_FOR')
    if http_x_forwarded_for:
        ip: str = http_x_forwarded_for.split(',')[0]
    else:
        ip: str = request.META.get('REMOTE_ADDR')
    return ip


def getUserAgent(request: HttpRequest) -> str:
    if request.META.get('HTTP_USER_AGENT'):
        return request.META.get('HTTP_USER_AGENT')
    return request.headers.get('User-Agent', 'Unknown')


# def resolvePageUrl(request: HttpRequest, page: str) -> str:
#     return f"{getUserGroupe(request).replace(' ', '')}:{page}"
