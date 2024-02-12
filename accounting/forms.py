from django import forms

from .models import Account, Bond

form_classes: str = 'form-control shadow-sm rounded'


class AccountForm(forms.ModelForm):
    
    class Meta:
            model = Account
            fields = [
                'account_type',
                'account_number',
                'account_holder_name',
                'bank_name',
                'account_status',
            ]
            widgets = {
                'account_type': forms.Select(
                    attrs={
                        'required': True,
                        'class': form_classes,
                    }
                ),
                'account_number': forms.TextInput(
                    attrs={
                        'required': True,
                        'class': form_classes,
                        'placeholder': 'رقم الحساب'
                    }
                ),
                'account_holder_name': forms.TextInput(
                    attrs={
                        'required': True,
                        'class': form_classes,
                        'placeholder': 'اسم صاحب الحساب'
                    }
                ),
                'bank_name': forms.TextInput(
                    attrs={
                        'required': True,
                        'class': form_classes,
                        'placeholder': 'اسم البنك'
                    }
                ),
                 'account_status': forms.Select(
                    attrs={
                        'required': True,
                        'class': form_classes,
                    }
                ),
            }
            labels = {
                'account_type': 'نوع الحساب',
                'account_number': 'رقم الحساب',
                'account_holder_name': 'اسم صاحب الحساب',
                'bank_name': 'اسم البنك',
                'account_status': 'حالة الحساب',
            }


