from django import forms
from django.forms import ModelForm

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

    class Meta:
        model = Person
        fields = [
            'name_ar',
            'name_en',
            'gender',
            'place_of_birth',
            'date_of_birth',
            'call_number',
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
                }
            ),
            'name_en': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'الاسم بالإنجليزي',
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
                    'placeholder': 'ex. +62 8123456789',
                    # 'pattern': "[+][0-9]{1,3} [0-9]{9,14}",
                    'type': 'tel',
                }
            ),
            'whatsapp_number': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'ex. +62 8123456789',
                    # 'pattern': "[+][0-9]{1,3} [0-9]{9,14}",
                    'type': 'tel',
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
