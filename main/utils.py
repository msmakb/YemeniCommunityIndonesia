import csv
import logging
from typing import Callable, Optional, Union

from django.contrib.auth.models import User
from django.core.exceptions import EmptyResultSet
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils.timezone import datetime

from . import constants
from .models import BaseModel

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


def exportAsCsv(
    queryset: QuerySet,
    fileName: Optional[str] = str(datetime.today()),
    fields: Optional[list[str] | str] = '__all__',
    labels_to_change: Optional[dict[str, str] | None] = None,
    values_to_change: Optional[dict[str, Callable] | None] = None,
    default_empty_value: Optional[str] = "-"
) -> HttpResponse:
    """
    Exports a given queryset to a CSV file, which can be downloaded by the user.

    :param queryset: The queryset to be exported. Must be a valid Django queryset.
    :type queryset: QuerySet
    :param fileName: The desired file name for the exported CSV file, without the file extension.
    :type fileName: str, optional
    :param fields: A list of fields that should be included in the exported CSV file. Can also be '__all__' to export all fields.
    :type fields: list[str] | str, optional
    :param labels_to_change: A dictionary where the keys are the original field names in the queryset and the values are the new labels to be used in the exported CSV file.
    :type labels_to_change: dict[str, str] | None, optional
    :param values_to_change: A dictionary where the keys are the original field names in the queryset and the values are callable functions to be applied to the field values before exporting. The callable function accepts one parameter which is the field need to be modified.
    :type values_to_change: dict[str, Callable] | None, optional
    :param default_empty_value: The value to be used for fields that are empty or None.
    :type default_empty_value: str, optional
    :raises EmptyResultSet: If the provided queryset is empty, a EmptyResultSet exception will be raised with the message "The queryset provided is empty."
    :return: A response object that can be used to download the exported CSV file.
    :rtype: HttpResponse

    """

    if not queryset.exists():
        raise EmptyResultSet("The queryset provided is empty.")

    if isinstance(fields, str):
        if fields == '__all__':
            fields = [field.name for field in queryset.first()._meta.get_fields()]
        else:
            fields = fields.split(' ')

    queryset: QuerySet[BaseModel] = queryset.values(*fields)
    response: HttpResponse = HttpResponse(
        content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{fileName}.csv"'
    writer = csv.writer(response)

    titles: list[str] = []
    if labels_to_change:
        for row in fields:
            titles.append(labels_to_change[row]
                          if row in labels_to_change else row)
    else:
        titles = fields

    writer.writerow([title.replace('_', " ").title() for title in titles])

    for model_row in queryset:
        row: list[str] = []
        for key, value in model_row.items():
            if not value:
                row.append(default_empty_value)
                continue
            if values_to_change and key in values_to_change:
                row.append(str(values_to_change[key](value)))
            else:
                row.append(str(value) if value else default_empty_value)
        writer.writerow(row)

    return response
