import django_filters
from django import forms
from django.db import models
from django.db.models.query import QuerySet
from main import constants

from .models import Person

form_class: str = 'form-control form-control-sm shadow-sm rounded'


class PersonFilter(django_filters.FilterSet):
    name_ar = django_filters.CharFilter(
        field_name='name_ar',
        lookup_expr='icontains',
        label='الاسم بالعربي',
        widget=forms.TextInput(
            attrs={
                'class': form_class,
                'placeholder': 'الاسم بالعربي',
            }
        )
    )
    name_en = django_filters.CharFilter(
        field_name='name_en',
        lookup_expr='icontains',
        label='الاسم بالإنجليزي',
        widget=forms.TextInput(
            attrs={
                'class': form_class,
                'placeholder': 'الاسم بالإنجليزي',
            }
        )
    )
    gender = django_filters.ChoiceFilter(
        field_name='gender',
        lookup_expr='iexact',
        label='الجنس',
        choices=constants.CHOICES.GENDER,
        widget=forms.Select(
            attrs={
                'class': form_class,
            }
        )
    )
    job_title = django_filters.ChoiceFilter(
        field_name='job_title',
        lookup_expr='iexact',
        label='المسمى الوظيفي',
        choices=constants.CHOICES.JOB_TITLE,
        widget=forms.Select(
            attrs={
                'class': form_class,
            }
        )
    )
    period_of_residence = django_filters.ChoiceFilter(
        field_name='period_of_residence',
        lookup_expr='iexact',
        label='فترة الإقامة',
        choices=constants.CHOICES.PERIOD_OF_RESIDENCE,
        widget=forms.Select(
            attrs={
                'class': form_class,
            }
        )
    )
    address__city = django_filters.ChoiceFilter(
        field_name='address__city',
        lookup_expr='iexact',
        label='المدينة',
        choices=constants.CHOICES.CITIES,
        widget=forms.Select(
            attrs={
                'class': form_class,
            }
        )
    )
    academic__academic_qualification = django_filters.ChoiceFilter(
        field_name='academic__academic_qualification',
        lookup_expr='iexact',
        label='المؤهل العلمي',
        choices=constants.CHOICES.ACADEMIC_QUALIFICATION,
        widget=forms.Select(
            attrs={
                'class': form_class,
            }
        )
    )
    membership__membership_type = django_filters.ChoiceFilter(
        field_name='membership__membership_type',
        lookup_expr='iexact',
        label='نوع العضوية',
        choices=constants.CHOICES.MEMBERSHIP_TYPE,
        widget=forms.Select(
            attrs={
                'class': form_class,
            }
        )
    )
    membership__card_number = django_filters.CharFilter(
        field_name='membership__card_number',
        lookup_expr='icontains',
        label='رقم البطاقة العضوية',
        widget=forms.TextInput(
            attrs={
                'class': form_class,
            }
        )
    )
    passport_number = django_filters.CharFilter(
        field_name='passport_number',
        lookup_expr='icontains',
        label='رقم الجواز',
        widget=forms.TextInput(
            attrs={
                'class': form_class,
            }
        )
    )
    filter_membership = django_filters.ChoiceFilter(
        field_name='filter_membership',
        lookup_expr='iexact',
        label='العضوية',
        method='filterMembership',
        choices=[
            ('0', 'الكل'),
            ('1', 'الأعضاء'),
            ('2', 'غير الأعضاء'),
        ],
        widget=forms.Select(
            attrs={
                'class': form_class,
            }
        )
    )

    def filterMembership(self, queryset: QuerySet, name: str, value: str):
        if value == '1':
            queryset = queryset.filter(membership__isnull=False)
        elif value == '2':
            queryset = queryset.filter(membership__isnull=True)
        return queryset

    class Meta:
        model = Person
        fields = [
            'name_ar',
            'name_en',
            'gender',
            'job_title',
            'period_of_residence',
            'address__city',
            'academic__academic_qualification',
            'membership__membership_type',
            'membership__card_number',
            'passport_number',
        ]
