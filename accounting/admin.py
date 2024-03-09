from django.contrib.admin import register, ModelAdmin

from .models import Account, Bond
from main.constants import BASE_MODEL_FIELDS, ROWS_PER_PAGE


@register(Account)
class AccountAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('id', 'account_type', 'account_number',
                                     'account_holder_name', 'bank_name',
                                     'account_status', *BASE_MODEL_FIELDS)
    list_filter: tuple[str, ...] = ('account_type', 'account_status',)
    search_fields: tuple[str, ...] = ('bank_name', 'account_status')
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS


@register(Bond)
class BondAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('id', 'bond_type', 'receiving_method',
                                     'reference_number', 'receiver_name',
                                     'receiver_account_number', 'sender_name',
                                     'sender_account_number', 'amount',
                                     'transfer_commission', 'receipt',
                                     'status', 'bond_date',
                                     *BASE_MODEL_FIELDS)
    list_filter: tuple[str, ...] = ('bond_type', 'status')
    search_fields: tuple[str, ...] = ('reference_number', 'receiver_name',
                                      'receiver_account_number', 'sender_name',
                                      'sender_account_number')
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS
