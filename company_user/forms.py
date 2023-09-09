import re
from typing import Any

from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm, UserChangeForm
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.db.utils import OperationalError

from main import constants

from .models import CompanyUser, Role

form_classes: str = 'form-control shadow-sm rounded'


class RoleForm(forms.ModelForm):

    def __init__(self, is_superuser, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not is_superuser:
            self.fields['groups'].queryset = Group.objects.all().exclude(
                name=constants.GROUPS.PARAMETER)

    class Meta:
        model = Role
        fields = [
            'name',
            'description',
            'groups',
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'أسم الوظيفة',
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'rows': 5,
                    'placeholder': 'الوصف',
                }
            ),
            'groups': forms.CheckboxSelectMultiple()
        }
        labels = {
            'name': 'أسم الوظيفة',
            'description': 'الوصف',
            'groups': 'الصلاحيات',
        }

    def clean_name(self):
        data = self.cleaned_data["name"]
        pattern = re.compile(r'^[\u0600-\u06FF\s]+$')
        if not pattern.match(data):
            raise forms.ValidationError(
                "يجب أن يحتوي هذا الحقل على أحرف عربية فقط")
        if len(data) < 3:
            raise forms.ValidationError(
                "يجب أن يحتوي أسم الوظيفة على 3 أحرف على الأقل")
        return data

    def clean_description(self):
        data = self.cleaned_data["description"]
        pattern = re.compile(r'^[\u0600-\u06FF\s]+$')
        if not pattern.match(data):
            raise forms.ValidationError(
                "يجب أن يحتوي هذا الحقل على أحرف عربية فقط")
        if len(data) < 10:
            raise forms.ValidationError(
                "يجب أن يحتوي الوصف على 10 أحرف على الأقل")
        return data

    def clean_groups(self):
        data = self.cleaned_data["groups"]
        if not data:
            raise forms.ValidationError(
                "يجب عليك إضافة صلاحية واحد على الأقل")

        return data


class CreateUserForm(UserCreationForm):
    try:
        role = forms.ChoiceField(
            label='الوظيفة',
            choices=[
                ('', '---------'),
                *[(role.pk, role)
                  for role in Role.getAll().exclude(name='superuser')],
                (0, 'مستخدم متميز'),
            ],
            widget=forms.Select(
                attrs={
                    'required': True,
                    'class': 'form-select shadow-sm rounded',
                }
            )
        )
    except OperationalError:
        pass

    def __init__(self, is_superuser: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not is_superuser:
            role_choices: list[tuple] = self.fields['role'].choices
            role_choices.pop()
            self.fields['role'].choices = role_choices
            self.fields['role'].widget.choices = role_choices

        self.fields['password1'].widget = forms.HiddenInput()
        self.fields['password2'].widget = forms.HiddenInput()

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
        ]
        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'الاسم الأول',
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'الاسم الأخير',
                }
            ),
            'email': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'عنوان البريد الإلكتروني',
                }
            ),
            'username': forms.HiddenInput(),
            'is_staff': forms.HiddenInput(),
        }
        labels = {
            'email': 'عنوان البريد الإلكتروني',
        }

    def clean_first_name(self):
        data = self.cleaned_data["first_name"]
        pattern = re.compile(r'^[\u0600-\u06FF\s]+$')
        if not pattern.match(data):
            raise forms.ValidationError(
                "يجب أن يحتوي هذا الحقل على أحرف عربية فقط")
        if len(data) < 3:
            raise forms.ValidationError(
                "يجب أن يحتوي الاسم الأول على 3 أحرف على الأقل")
        return data

    def clean_last_name(self):
        data = self.cleaned_data["last_name"]
        pattern = re.compile(r'^[\u0600-\u06FF\s]+$')
        if not pattern.match(data):
            raise forms.ValidationError(
                "يجب أن يحتوي هذا الحقل على أحرف عربية فقط")
        if len(data) < 3:
            raise forms.ValidationError(
                "يجب أن يحتوي الاسم الأول على 3 أحرف على الأقل")
        return data

    def clean_email(self):
        data = self.cleaned_data["email"]
        if not data:
            raise forms.ValidationError("هذا الحقل مطلوب.")

        if User.objects.filter(email=data).exists():
            raise forms.ValidationError(
                "عنوان البريد الإلكتروني هذا موجود بالفعل")

        return data


class SetUsernameAndPasswordForm(SetPasswordForm):
    username = forms.CharField(
        max_length=50,
        label='اسم المستخدم',
        validators=[ASCIIUsernameValidator()],
        widget=forms.TextInput(
            attrs={
                'required': True,
                'class': form_classes,
                'placeholder': 'اسم المستخدم',
                "autocomplete": "off"
            }
        )
    )

    field_order = ['username', 'new_password1', 'new_password2']

    class Meta:
        model = User
        fields = ['new_password1', 'new_password2']

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        pass_widget = forms.PasswordInput(
            attrs={
                'required': True,
                'class': 'form-control form-control-lg',
                'placeholder': 'كلمة المرور',
                "autocomplete": "new-password"
            }
        )

        self.fields['new_password1'].widget = pass_widget
        self.fields['new_password2'].widget = pass_widget

    def clean_username(self):
        data = self.cleaned_data["username"]
        if User.objects.filter(username=data).exists():
            raise forms.ValidationError(
                "اسم المستخدم مرفوض. يرجى التغيير إلى اسم مستخدم مختلف")

        return data

    def save(self, commit: bool = ...) -> Any:
        self.user.username = self.cleaned_data['username']
        self.user.is_active = True
        return super().save(commit)


class ChangeUserDataForm(UserChangeForm):
    try:
        role = forms.ChoiceField(
            label='الوظيفة',
            choices=[
                ('', '---------'),
                *[(role.pk, role)
                  for role in Role.getAll().exclude(name='superuser')],
                (0, 'مستخدم متميز'),
            ],
            widget=forms.Select(
                attrs={
                    'required': True,
                    'class': 'form-select shadow-sm rounded',
                }
            )
        )
    except OperationalError:
        pass

    field_order = ['first_name', 'last_name', 'email', 'role', 'is_active']

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        del self.fields['is_active'].widget.choices[0]
        del self.fields['password']

        role_id: int = -1
        if self.instance.is_superuser:
            role_id = 0
        else:
            role_id = CompanyUser.get(user=self.instance).role.pk
        self.fields['role'].initial = role_id

        if self.instance.username == 'admin':
            self.fields['role'].choices = self.fields['role'].choices[-1:]
            self.fields['role'].widget.choices = self.fields['role'].choices[-1:]
            del self.fields['is_active'].widget.choices[-1]

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'is_active'
        ]
        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'الاسم الأول',
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'الاسم الأخير',
                }
            ),
            'email': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'عنوان البريد الإلكتروني',
                }
            ),
            'is_active': forms.NullBooleanSelect(
                attrs={
                    'required': True,
                    'class': 'form-select shadow-sm rounded',
                }
            ),
        }

    def clean_first_name(self):
        data = self.cleaned_data["first_name"]
        pattern = re.compile(r'^[\u0600-\u06FF\s]+$')
        if not pattern.match(data):
            raise forms.ValidationError(
                "يجب أن يحتوي هذا الحقل على أحرف عربية فقط")
        if len(data) < 3:
            raise forms.ValidationError(
                "يجب أن يحتوي الاسم الأول على 3 أحرف على الأقل")
        return data

    def clean_last_name(self):
        data = self.cleaned_data["last_name"]
        pattern = re.compile(r'^[\u0600-\u06FF\s]+$')
        if not pattern.match(data):
            raise forms.ValidationError(
                "يجب أن يحتوي هذا الحقل على أحرف عربية فقط")
        if len(data) < 3:
            raise forms.ValidationError(
                "يجب أن يحتوي الاسم الأول على 3 أحرف على الأقل")
        return data

    def clean_email(self):
        data = self.cleaned_data["email"]
        if not data:
            raise forms.ValidationError("هذا الحقل مطلوب.")

        if User.objects.filter(email=data).exists():
            raise forms.ValidationError(
                "عنوان البريد الإلكتروني هذا موجود بالفعل")

        return data
