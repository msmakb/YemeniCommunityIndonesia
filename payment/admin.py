from django.contrib.admin import ModelAdmin, register

from main.constants import BASE_MODEL_FIELDS, ROWS_PER_PAGE

from .models import MembershipPayment


@register(MembershipPayment)
class MembershipPaymentAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('id', )
