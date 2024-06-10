from django.contrib.admin import ModelAdmin, register

from main.constants import BASE_MODEL_FIELDS, ROWS_PER_PAGE

from .models import CustomFormItem, CustomFormResponse


@register(CustomFormItem)
class CustomFormItemAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('formId', 'index', 'itemId', 'itemType', 'title',
                                     'description', 'itemData',
                                     *BASE_MODEL_FIELDS)
    search_fields: tuple[str, ...] = ('formId',)
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS


@register(CustomFormResponse)
class CustomFormResponseAdmin(ModelAdmin):
    list_display: tuple[str, ...] = (
        'responseId', 'answers', *BASE_MODEL_FIELDS)
    search_fields: tuple[str, ...] = ('responseId',)
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS
