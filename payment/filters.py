import django_filters
from django import forms
from django.db.models.query import QuerySet
from main import constants

from .models import MembershipPayment

form_class: str = 'form-control form-control-sm shadow-sm rounded'


class MembershipPaymentFilter(django_filters.FilterSet):
    membership__card_number = django_filters.CharFilter(
        field_name='membership__card_number',
        lookup_expr='icontains',
        label='رقم البطاقة',
        widget=forms.TextInput(
            attrs={
                'class': form_class,
                'placeholder': 'رقم البطاقة	',
            }
        )
    )
    reference_number = django_filters.CharFilter(
        field_name='reference_number',
        lookup_expr='icontains',
        label='رقم المرجع',
        widget=forms.TextInput(
            attrs={
                'class': form_class,
                'placeholder': 'رقم المرجع',
            }
        )
    )
    status = django_filters.ChoiceFilter(
        field_name='status',
        lookup_expr='iexact',
        label='الحالة',
        choices=constants.CHOICES.PAYMENT_STATUS[1:],
        widget=forms.Select(
            attrs={
                'class': form_class,
            }
        )
    )

    class Meta:
        model = MembershipPayment
        fields = [
            'membership__card_number',
            'reference_number',
            'status',
        ]
