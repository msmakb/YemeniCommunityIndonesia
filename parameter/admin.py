from django.contrib.admin import ModelAdmin, register
from django.db.models.query import QuerySet
from django.http import HttpRequest

from main.constants import BASE_MODEL_FIELDS, ROWS_PER_PAGE, ACCESS_TYPE
from .models import Parameter, ImageParameter


@register(Parameter)
class ParameterAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('parameter', 'value', 'description',
                                     *BASE_MODEL_FIELDS)
    list_filter: tuple[str, ...] = ('updated',)
    search_fields: tuple[str, ...] = ('name', 'value')
    ordering: tuple[str, ...] = ('name',)
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS

    def parameter(self, obj: Parameter) -> str:
        return obj.__str__()

    def get_queryset(self, request: HttpRequest) -> QuerySet[Parameter]:
        queryset: QuerySet[Parameter] = super().get_queryset(request)
        return queryset.filter(access_type=ACCESS_TYPE.ADMIN_ACCESS)

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False

    def has_delete_permission(self, *args, **kwargs) -> bool:
        return False


@register(ImageParameter)
class ImageParameterAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('file_name', 'content',
                                     *BASE_MODEL_FIELDS)
    list_filter: tuple[str, ...] = ('updated',)
    search_fields: tuple[str, ...] = ('file_name',)
    ordering: tuple[str, ...] = ('-updated',)
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS
