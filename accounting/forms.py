from typing import Any
from django import forms
from django.db.models.query import Q
from django.forms.fields import Field

from main import constants

from .models import Account, Bond

form_classes: str = "form-control shadow-sm rounded"


class DateInput(forms.DateInput):
    input_type: str = "date"


class AccountForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = [
            "account_type",
            "account_number",
            "account_holder_name",
            "bank_name",
            "account_status",
        ]
        widgets = {
            "account_type": forms.Select(
                attrs={
                    "required": True,
                    "class": form_classes,
                }
            ),
            "account_number": forms.TextInput(
                attrs={
                    "required": True,
                    "class": form_classes,
                    "placeholder": "رقم الحساب",
                }
            ),
            "account_holder_name": forms.TextInput(
                attrs={
                    "required": True,
                    "class": form_classes,
                    "placeholder": "اسم صاحب الحساب",
                }
            ),
            "bank_name": forms.TextInput(
                attrs={
                    "required": True,
                    "class": form_classes,
                    "placeholder": "اسم البنك",
                }
            ),
            "account_status": forms.Select(
                attrs={
                    "required": True,
                    "class": form_classes,
                }
            ),
        }
        labels = {
            "account_type": "نوع الحساب",
            "account_number": "رقم الحساب",
            "account_holder_name": "اسم صاحب الحساب",
            "bank_name": "اسم البنك",
            "account_status": "حالة الحساب",
        }


class BondForm(forms.ModelForm):

    receiver_account: str = forms.ChoiceField(
        required=False,
        label="حساب المستلم",
        widget=forms.Select(
            attrs={
                "required": False,
                "class": form_classes,
            }
        ),
    )

    sender_account: str = forms.ChoiceField(
        required=False,
        label="حساب المرسل",
        widget=forms.Select(
            attrs={
                "required": False,
                "class": form_classes,
            }
        ),
    )

    class Meta:
        model = Bond
        fields = [
            "bond_type",
            "receiving_method",
            "sender_account",
            "sender_name",
            "sender_account_number",
            "receiver_account",
            "receiver_name",
            "receiver_account_number",
            "bond_date",
            "amount",
            "transfer_commission",
            "receipt",
            "bond_description",
        ]
        widgets = {
            "bond_type": forms.Select(
                attrs={
                    "required": False,
                    "class": form_classes,
                }
            ),
            "receiving_method": forms.Select(
                attrs={
                    "required": True,
                    "class": form_classes,
                }
            ),
            "receiver_name": forms.TextInput(
                attrs={
                    "required": False,
                    "class": form_classes,
                    "placeholder": "اسم المستلم",
                }
            ),
            "receiver_account_number": forms.TextInput(
                attrs={
                    "required": False,
                    "class": form_classes,
                    "placeholder": "رقم حساب المستلم",
                }
            ),
            "sender_name": forms.TextInput(
                attrs={
                    "required": False,
                    "class": form_classes,
                    "placeholder": "اسم المرسل",
                }
            ),
            "sender_account_number": forms.TextInput(
                attrs={
                    "required": False,
                    "class": form_classes,
                    "placeholder": "رقم حساب المرسل",
                }
            ),
            "bond_date": DateInput(
                attrs={
                    "required": True,
                    "class": form_classes,
                    "data-provide": "datepicker",
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "required": True,
                    "class": form_classes,
                    "placeholder": "المبلغ",
                    "step": "any",
                }
            ),
            "transfer_commission": forms.NumberInput(
                attrs={
                    "required": True,
                    "class": form_classes,
                    "placeholder": "عمولة التحويل",
                }
            ),
            "receipt": forms.FileInput(
                attrs={
                    "required": True,
                    "class": form_classes,
                    "accept": ".jpg, .jpeg, .png, .gif, .svg, "
                    + ".bmp, .webp, .pdf, .doc, .docx",
                }
            ),
            "bond_description": forms.Textarea(
                attrs={
                    "required": False,
                    "class": form_classes,
                    "rows": 5,
                    "placeholder": "الوصف",
                }
            ),
        }
        labels = {
            "bond_type": "نوع السند",
            "receiving_method": "نوع المعاملة",
            "receiver_account": "حساب المستلم",
            "receiver_name": "اسم المستلم",
            "receiver_account_number": "رقم حساب المستلم",
            "sender_account": "حساب المرسل",
            "sender_name": "اسم المرسل",
            "sender_account_number": "رقم حساب المرسل",
            "bond_date": "تاريخ السند",
            "amount": "المبلغ",
            "transfer_commission": "عمولة التحويل",
            "receipt": "الفاتورة",
            "bond_description": "الوصف",
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        account_choices = (
            ("", "---------"),
            *[
                (
                    account.id,
                    f"{account.account_holder_name} - {account.account_number}",
                )
                for account in Account.filter(
                    ~Q(account_status=constants.ACCOUNT_STATUS.OUT_SERVICE)
                )
            ],
        )

        form_fields: dict[str, type[Field]] = self.fields
        form_fields["receiver_account"].choices = account_choices
        form_fields["receiver_account"].widget.choices = account_choices
        form_fields["sender_account"].choices = account_choices
        form_fields["sender_account"].widget.choices = account_choices
        form_fields["receiver_name"].required = False
        form_fields["receiver_account_number"].required = False
        form_fields["sender_name"].required = False
        form_fields["sender_account_number"].required = False

    def clean(self) -> dict[str, Any]:
        cleaned_data: dict[str, Any] = super().clean()

        bond_type: str = cleaned_data.get("bond_type", "")
        if bond_type == constants.BOND_TYPE.INCOMING:
            receiver_account_id: str = cleaned_data["receiver_account"]
            receiver_account: Account = Account.get(id=receiver_account_id)
            cleaned_data["receiver_name"] = receiver_account.account_holder_name
            cleaned_data["receiver_account_number"] = receiver_account.account_number
        elif bond_type == constants.BOND_TYPE.OUTGOING:
            sender_account_id: str = cleaned_data["sender_account"]
            sender_account: Account = Account.get(id=sender_account_id)
            cleaned_data["sender_name"] = sender_account.account_holder_name
            cleaned_data["sender_account_number"] = sender_account.account_number
        elif bond_type == constants.BOND_TYPE.MOVING:
            receiver_account_id: str = cleaned_data["receiver_account"]
            receiver_account: Account = Account.get(id=receiver_account_id)
            cleaned_data["receiver_name"] = receiver_account.account_holder_name
            cleaned_data["receiver_account_number"] = receiver_account.account_number

            sender_account_id: str = cleaned_data["sender_account"]
            sender_account: Account = Account.get(id=sender_account_id)
            cleaned_data["sender_name"] = sender_account.account_holder_name
            cleaned_data["sender_account_number"] = sender_account.account_number
        else:
            self.add_error("bond_type", "قيمة غير صالحة")

        return cleaned_data
