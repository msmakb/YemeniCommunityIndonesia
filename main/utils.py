import csv
import logging
import six
from threading import Thread
from typing import Any, Callable, Iterable, Optional, Protocol, Union
from uuid import uuid4

from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet

from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import EmptyResultSet
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils.timezone import datetime

from . import constants
from .models import AuditEntry, BaseModel

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


def exportAsCsvExcel(
    queryset: QuerySet,
    fileName: Optional[str] = str(datetime.today()),
    fields: Optional[list[str] | str] = '__all__',
    labels_to_change: Optional[dict[str, str] | None] = None,
    values_to_change: Optional[dict[str, Callable] | None] = None,
    default_empty_value: Optional[str] = "-",
    sheet_type: Optional[str] = 'csv'
) -> HttpResponse:
    """
    Exports a given queryset to a CSV/EXCEL file, which can be downloaded by the user.

    :param queryset: The queryset to be exported. Must be a valid Django queryset.
    :type queryset: QuerySet
    :param fileName: The desired file name for the exported CSV/EXCEL file, without the file extension.
    :type fileName: str, optional
    :param fields: A list of fields that should be included in the exported CSV/EXCEL file. Can also be '__all__' to export all fields.
    :type fields: list[str] | str, optional
    :param labels_to_change: A dictionary where the keys are the original field names in the queryset and the values are the new labels to be used in the exported CSV/EXCEL file.
    :type labels_to_change: dict[str, str] | None, optional
    :param values_to_change: A dictionary where the keys are the original field names in the queryset and the values are callable functions to be applied to the field values before exporting. The callable function accepts one parameter which is the field need to be modified.
    :type values_to_change: dict[str, Callable] | None, optional
    :param default_empty_value: The value to be used for fields that are empty or None.
    :type default_empty_value: str, optional
    :param sheet_type: The file type, excel or CSV, the default value is CSV.
    :type sheet_type: str, optional
    :raises EmptyResultSet: If the provided queryset is empty, a EmptyResultSet exception will be raised with the message "The queryset provided is empty."
    :return: A response object that can be used to download the exported CSV/EXCEL file.
    :rtype: HttpResponse

    """
    class CsvWriter(Protocol):
        def writerow(self, row: Iterable[Any]) -> Any: ...
        def writerows(self, rows: Iterable[Iterable[Any]]) -> None: ...

    if not queryset.exists():
        raise EmptyResultSet("The queryset provided is empty.")

    if isinstance(fields, str):
        if fields == '__all__':
            fields = [field.name for field in queryset.first()._meta.get_fields()]
        else:
            fields = fields.split(' ')

    titles: list[str] = []
    if labels_to_change:
        for row in fields:
            titles.append(labels_to_change[row]
                          if row in labels_to_change else row)
    else:
        titles = fields
    titles = [title.replace('_', " ").title() for title in titles]

    sheet: CsvWriter | Worksheet = None

    is_excel_file: bool = True if sheet_type.lower() == 'excel' else False
    if is_excel_file:
        response = HttpResponse(
            content_type=constants.MIME_TYPE.MS_EXCEL_OPEN_XML)
        response["Content-Disposition"] = f'attachment; filename="{fileName}.xlsx"'
        workbook: Workbook = Workbook()
        sheet = workbook.active
        sheet.append(titles)
    else:
        response: HttpResponse = HttpResponse(
            content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{fileName}.csv"'
        sheet = csv.writer(response)
        sheet.writerow(titles)

    queryset: QuerySet[BaseModel] = queryset.values(*fields)
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
        if is_excel_file:
            sheet.append(row)
        else:
            sheet.writerow(row)

    if is_excel_file:
        table = Table(displayName="Table", ref=sheet.dimensions)
        style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False, showLastColumn=False,
                               showRowStripes=True, showColumnStripes=False)
        table.tableStyleInfo = style
        sheet.add_table(table)
        workbook.save(response)

    return response


def generateRandomString() -> str:
    return str(uuid4()).rsplit('-', maxsplit=1).pop().upper()


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )


account_activation_token = AccountActivationTokenGenerator()


def logUserActivity(request: HttpRequest | None, activity_type: str, details: Optional[str] = None) -> None:
    if request is None:
        AuditEntry.create(
            ip='0.0.0.0',
            user_agent='-',
            action=activity_type,
            username=details[:100]
        )
    else:
        AuditEntry.create(
            ip=getClientIp(request),
            user_agent=getUserAgent(request),
            action=activity_type,
            username=details[:100]
        )


def sendEmail(email_message: EmailMessage) -> None:
    thread: Thread = Thread(
        target=lambda email_message: email_message.send(),
        args=[email_message])
    thread.start()
