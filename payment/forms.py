from django import forms

from .models import MembershipPayment

form_classes: str = 'form-control shadow-sm rounded'


class MembershipPaymentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = MembershipPayment
        fields = [
            'number_of_months',
            'receipt',
            'amount',
            'membership',
            'from_month',
        ]
        widgets = {
            'number_of_months': forms.NumberInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'min': 1,
                    'max': 24,
                    'placeholder': 'أدخل عدد الأشهر المراد دفعها',
                }
            ),
            'receipt': forms.FileInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'disabled': True,
                    'accept': '.png, .jpeg, .jpg'
                }
            ),
            'amount': forms.HiddenInput(),
            'membership': forms.HiddenInput(),
            'from_month': forms.HiddenInput(),
            'member_note': forms.HiddenInput(),
        }
        labels = {
            'number_of_months': 'عدد الأشهر',
            'receipt': 'الإيصال',
        }
