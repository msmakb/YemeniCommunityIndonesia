from django.contrib.admin import ModelAdmin, register

from .constants import BASE_MODEL_FIELDS, ROWS_PER_PAGE, BLOCK_TYPES
from .models import AuditEntry, BlockedClient


@register(AuditEntry)
class AuditEntryAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('action_type', 'user_agent', 'username', 'ip',
                                     *BASE_MODEL_FIELDS)
    list_filter: tuple[str, ...] = ('action', 'created',)
    search_fields: tuple[str, ...] = ('action', 'user_agent', 'username', 'ip')
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False

    def has_change_permission(self, *args, **kwargs) -> bool:
        return False


@register(BlockedClient)
class BlockedClientAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('user_agent', 'ip', 'blockType',
                                     'blocked_times', *BASE_MODEL_FIELDS)
    list_filter: tuple[str, ...] = ('created',)
    search_fields: tuple[str, ...] = ('user_agent', 'ip')
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS

    def blockType(self, obj: BlockedClient) -> str:
        match obj.block_type:
            case BLOCK_TYPES.UNBLOCKED:
                return 'ملغى حظره'
            case BLOCK_TYPES.TEMPORARY:
                return 'مؤقت'
            case BLOCK_TYPES.INDEFINITELY:
                return 'مؤبد'

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False
