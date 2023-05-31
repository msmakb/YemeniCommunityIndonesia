from django.contrib.admin import ModelAdmin, register

from main.constants import BASE_MODEL_FIELDS, ROWS_PER_PAGE, BLOCK_TYPES
from .models import CompanyUser, Role


@register(CompanyUser)
class CompanyUserAdmin(ModelAdmin):
    pass
    # list_display: tuple[str, ...] = ('action_type', 'user_agent', 'username', 'ip',
    #                                  *BASE_MODEL_FIELDS)
    # list_filter: tuple[str, ...] = ('action', 'created',)
    # search_fields: tuple[str, ...] = ('action', 'user_agent', 'username', 'ip')
    # list_per_page: int = ROWS_PER_PAGE
    # exclude: tuple[str, ...] = BASE_MODEL_FIELDS

    # def has_add_permission(self, *args, **kwargs) -> bool:
    #     return False

    # def has_change_permission(self, *args, **kwargs) -> bool:
    #     return False


@register(Role)
class RoleAdmin(ModelAdmin):
    pass
