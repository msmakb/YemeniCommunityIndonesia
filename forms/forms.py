from copy import copy
from django import forms

from main import constants

form_classes: str = 'form-control shadow-sm rounded'


class CustomFormItemForm(forms.Form):
    itemTypeChoices: list[tuple[str, str]] = copy(
        constants.CHOICES.CUSTOM_FORM_ITEM_TYPE)
    itemTypeChoices.insert(0, (None, "---------"))
    itemType: str = forms.ChoiceField(
        required=True,
        choices=itemTypeChoices,
        label="نوع الحقل",
        widget=forms.Select(
            attrs={
                'required': True,
                'class': form_classes,
            }
        ),
    )

    title: str = forms.CharField(
        required=False,
        label="السؤال",
        widget=forms.TextInput(
            attrs={
                'required': False,
                'class': form_classes,
                'placeholder': 'السؤال',
            }
        ),
    )

    description: str = forms.CharField(
        required=False,
        label="الوصف",
        widget=forms.TextInput(
            attrs={
                'required': False,
                'class': form_classes,
                'placeholder': 'الوصف',
            }
        ),
    )

    required: bool = forms.BooleanField(
        required=False,
        label="حقل مطلوب",
        widget=forms.CheckboxInput(
            attrs={
                "required": False,
                "class": "form-check-input check-box-ar-input",
            }
        ),
    )

    autofill: bool = forms.BooleanField(
        required=False,
        label="الملء التلقائي والتحقق من صحة الإدخال",
        widget=forms.CheckboxInput(
            attrs={
                "required": False,
                "class": "form-check-input check-box-ar-input",
            }
        ),
    )

    isHidden: bool = forms.BooleanField(
        required=False,
        label="إخفاء الحقل",
        widget=forms.CheckboxInput(
            attrs={
                "required": False,
                "disabled": True,
                "class": "form-check-input check-box-ar-input",
            }
        ),
    )

    headerImg: str = forms.ImageField(
        required=False,
        label="صورة العنوان",
        widget=forms.FileInput(
            attrs={
                "required": False,
                "class": form_classes,
                'accept': '.png, .jpeg, .jpg',
            }
        ),
    )
