import re
from typing import Any

from django import forms
from django.forms import ModelForm
from django.utils import timezone

from main.constants import PHONE_NUMBERS_COUNTRY_CODES

from .models import Academic, Address, FamilyMembers, Person

form_classes: str = 'form-control shadow-sm rounded'


class DateInput(forms.DateInput):
    input_type: str = 'date'


class FamilyMembersForm(ModelForm):

    class Meta:
        model = FamilyMembers
        fields = [
            'family_name',
            'member_count',
        ]
        widgets = {
            'family_name': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'آل ..',
                }
            ),
            'member_count': forms.NumberInput(
                attrs={
                    'value': 0,
                    'required': True,
                    'class': form_classes,
                    'placeholder': '0',
                }
            ),
        }
        labels = {
            'family_name': 'الأسم العائلي',
            'member_count': 'عدد أفراد الأسرة التي تعيلها في إندونيسيا'
        }

    def clean_member_count(self):
        data = self.cleaned_data.get("member_count")
        if data > 20:
            raise forms.ValidationError('أدخل رقما صحيحا.')

        return data


class AddressForm(ModelForm):

    class Meta:
        model = Address
        fields = [
            'street_address',
            'district',
            'city',
            'province',
            'postal_code'
        ]
        widgets = {
            'street_address': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'ex. Jl. ABC No.5',
                }
            ),
            'district': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'ex. ABC',
                }
            ),
            'city': forms.Select(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'ex. Jakarta',
                }
            ),
            'province': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'ex. Jawa Barat',
                }
            ),
            'postal_code': forms.TextInput(
                attrs={
                    'required': False,
                    'class': form_classes,
                    'placeholder': 'ex. 012345',
                }
            ),
        }
        labels = {
            'street_address': 'عنوان الشارع',
            'district': 'المنطقة',
            'city': 'المدينة',
            'province': 'الولاية',
            'postal_code': 'الرمز البريدي (إختياري)'
        }


class AcademicForm(ModelForm):

    class Meta:
        model = Academic
        fields = [
            'academic_qualification',
            'school',
            'major',
            'semester'
        ]
        widgets = {
            'academic_qualification': forms.Select(
                attrs={
                    'required': True,
                    'class': form_classes,
                }
            ),
            'school': forms.TextInput(
                attrs={
                    'required': False,
                    'class': form_classes,
                    'placeholder': 'ex. Yemeni University',
                }
            ),
            'major': forms.TextInput(
                attrs={
                    'required': False,
                    'class': form_classes,
                    'placeholder': 'ex. IT',
                }
            ),
            'semester': forms.NumberInput(
                attrs={
                    'required': False,
                    'class': form_classes,
                    'placeholder': '4',
                }
            ),
        }
        labels = {
            'academic_qualification': 'المؤهل العلمي',
            'school': 'أسم الجامعة / معهد / مدرسة (إختياري)',
            'major': 'التخصص الدراسي (إختياري)',
            'semester': 'الفصل الدراسي (إختياري)',
        }


class AddPersonForm(ModelForm):
    country_code_choices: list[tuple[str, str]] = [
        (code, f"{country} (+{code})") for country, code in PHONE_NUMBERS_COUNTRY_CODES.items()
    ]
    country_code1 = forms.ChoiceField(
        label="المفتاح",
        choices=country_code_choices,
        initial='62',
        widget=forms.Select(
            attrs={
                'required': True,
                'class': form_classes,
            }
        )
    )
    country_code2 = forms.ChoiceField(
        label="المفتاح",
        choices=country_code_choices,
        initial='62',
        widget=forms.Select(
            attrs={
                'required': True,
                'class': form_classes,
            }
        )
    )

    class Meta:
        model = Person
        fields = [
            'name_ar',
            'name_en',
            'gender',
            'place_of_birth',
            'date_of_birth',
            # 'country_code1',
            'call_number',
            # 'country_code2',
            'whatsapp_number',
            'email',
            'job_title',
            'period_of_residence',
            'photograph',
            'passport_photo',
            'residency_photo',
        ]
        widgets = {
            'name_ar': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'الاسم بالعربي',
                    'pattern': r'^[\u0600-\u06FF\s]+$'
                }
            ),
            'name_en': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'الاسم بالإنجليزي',
                    'pattern': r'^[A-Za-z\s]+$'
                }
            ),
            'gender': forms.Select(
                attrs={
                    'required': True,
                    'class': form_classes,
                }
            ),
            'place_of_birth': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'صنعاء، حضرموت ... ',
                    'pattern': r'^[\u0600-\u06FF\s,-]+$'
                }
            ),
            'date_of_birth': DateInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'data-provide': 'datepicker',
                }
            ),
            'call_number': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'ex. 8123456789',
                    'type': 'tel',
                    'pattern': r'^\d{9,15}$',
                }
            ),
            'whatsapp_number': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'ex. 8123456789',
                    'type': 'tel',
                    'pattern': r'^\d{9,15}$',
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'ex. yemeni@indonesia.com',
                }
            ),
            'job_title': forms.Select(
                attrs={
                    'required': True,
                    'class': form_classes,
                }
            ),
            'period_of_residence': forms.Select(
                attrs={
                    'required': True,
                    'class': form_classes,
                }
            ),
            'photograph': forms.FileInput(
                attrs={
                    'required': False,
                    'class': form_classes,
                    'accept': '.png, .jpeg, .jpg'
                }
            ),
            'passport_photo': forms.FileInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'accept': '.png, .jpeg, .jpg'
                }
            ),
            'residency_photo': forms.FileInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'accept': '.png, .jpeg, .jpg'
                }
            )
        }
        labels = {
            'name_ar': 'الاسم كاملاًً بالعربي مطابقاً للجواز',
            'name_en': 'الاسم كاملاًً بالإنجليزي مطابقاً للجواز',
            'gender': 'الجنس',
            'place_of_birth': 'مكان الميلاد مطابقاً للجواز',
            'date_of_birth': 'تاريخ الميلاد مطابقاً للجواز',
            'call_number': 'رقم الهاتف (اتصال)',
            'whatsapp_number': 'رقم الواتساب',
            'email': 'البريد الإلكتروني',
            'job_title': 'المسمى الوظيفي',
            'period_of_residence': 'فترة الإقامة في إندونيسيا',
            'photograph': 'صورة شخصية (إلزامي للرجال إختياري للنساء)',
            'passport_photo': 'صورة جواز السفر',
            'residency_photo': 'صورة الإقامة أو مايثبت تواجدك في جمهورية إندونيسيا',
        }

    def clean_name_ar(self):
        data = self.cleaned_data.get('name_ar')
        pattern = re.compile(r'^[\u0600-\u06FF\s]+$')
        if not pattern.match(data):
            raise forms.ValidationError(
                "يجب أن يحتوي هذا الحقل على أحرف عربية فقط")
        if len(data) < 10:
            raise forms.ValidationError(
                "يجب أن يحتوي الاسم على 10 أحرف على الأقل")
        return data

    def clean_name_en(self):
        data = self.cleaned_data.get('name_en')
        pattern = re.compile(r'^[A-Za-z\s]+$')
        if not pattern.match(data):
            raise forms.ValidationError(
                "يجب أن يحتوي هذا الحقل على أحرف إنجليزية فقط")
        if len(data) < 10:
            raise forms.ValidationError(
                "يجب أن يحتوي الاسم على 10 أحرف على الأقل")
        return data

    def clean_place_of_birth(self):
        data = self.cleaned_data.get('place_of_birth')
        pattern = re.compile(r'^[\u0600-\u06FF\s,-]+$')
        if not pattern.match(data):
            raise forms.ValidationError(
                "يجب كتابة مكان الميلاد باللغة العربية")
        return data

    def clean_date_of_birth(self):
        data = self.cleaned_data.get('date_of_birth')
        age = timezone.now().year - data.year
        if age < 15:
            raise forms.ValidationError("يجب أن يكون عمرك 15 عامًا على الأقل")
        return data

    def clean_call_number(self) -> str:
        call_number: str = self.cleaned_data.get("call_number")
        country_code: str = self.cleaned_data.get("country_code1")
        if call_number.startswith('00') or call_number.startswith("+"):
            raise forms.ValidationError(
                "يجب عدم إدخال المفتاح الدولي في هذا الحقل")
        pattern = re.compile(r'^\d{9,15}$')
        if not pattern.match(call_number) or len(call_number) < 9:
            raise forms.ValidationError("رقم الهاتف غير صحيح")

        return call_number

    def clean_whatsapp_number(self) -> str:
        whatsapp_number: str = self.cleaned_data.get("whatsapp_number")
        country_code: str = self.cleaned_data.get("country_code2")
        if whatsapp_number.startswith('00') or whatsapp_number.startswith("+"):
            raise forms.ValidationError(
                "يجب عدم إدخال المفتاح الدولي في هذا الحقل")
        pattern = re.compile(r'^\d{9,15}$')
        if not pattern.match(whatsapp_number) or len(whatsapp_number) < 9:
            raise forms.ValidationError("رقم الهاتف غير صحيح")

        return whatsapp_number

    def clean(self) -> dict[str, Any]:
        cleaned_data: dict[str, Any] = super().clean()
        cleaned_data['call_number'] = f"+({cleaned_data['country_code1']}) {cleaned_data['call_number']}"
        cleaned_data['whatsapp_number'] = f"+({cleaned_data['country_code2']}) {cleaned_data['whatsapp_number']}"
        return cleaned_data
