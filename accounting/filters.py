import django_filters
from django import forms
from main import constants

from .models import Bond

class DateRangeWidget(django_filters.widgets.DateRangeWidget):

    def __init__(self, from_attrs=None, to_attrs=None, attrs=None):
        super(DateRangeWidget, self).__init__(attrs)
        self.widgets[0].input_type = 'date'
        self.widgets[1].input_type = 'date'
        
        if from_attrs:
            self.widgets[0].attrs.update(from_attrs)
        if to_attrs:
            self.widgets[1].attrs.update(to_attrs)

form_class: str = 'form-control form-control-sm shadow-sm rounded'


class BondFilter(django_filters.FilterSet):
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
    bond_type = django_filters.ChoiceFilter(
        field_name='bond_type',
        lookup_expr='iexact',
        label='نوع السند',
        choices=constants.CHOICES.BOND_TYPE,
        widget=forms.Select(
            attrs={
                'class': form_class,
            }
        )
    )
    status = django_filters.ChoiceFilter(
        field_name='status',
        lookup_expr='iexact',
        label='الحالة',
        choices=constants.CHOICES.BOND_STATUS,
        widget=forms.Select(
            attrs={
                'class': form_class,
            }
        )
    )
    bond_date = django_filters.DateFromToRangeFilter(
        field_name='bond_date',
        label='تاريخ السند',
        widget=DateRangeWidget(
            from_attrs={
                'class': form_class, 
                'data-provide':'datepicker'
            },
            to_attrs={
                'class': form_class, 
                'data-provide':'datepicker'
            }
        )
    )
    receiver_account_number = django_filters.CharFilter(
        field_name='receiver_account_number',
        lookup_expr='icontains',
        label='رقم حساب المستلم',
        widget=forms.TextInput(
            attrs={
                'class': form_class,
                'placeholder': 'رقم حساب المستلم',
            }
        )
    )
    sender_account_number = django_filters.CharFilter(
        field_name='sender_account_number',
        lookup_expr='icontains',
        label='رقم حساب المرسل	',
        widget=forms.TextInput(
            attrs={
                'class': form_class,
                'placeholder': 'رقم حساب المرسل	',
            }
        )
    )
    class Meta:
        model = Bond
        fields = [
            'reference_number',
            'bond_type',
            'status',
            'bond_date',
            'receiver_account_number',
            'sender_account_number',
        ]
