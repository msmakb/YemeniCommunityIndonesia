from __future__ import annotations
from os import path
from uuid import uuid4

from django.db import models
from django.db.models.fields.files import ImageFieldFile
from django.utils.timezone import datetime

from main.models import BaseModel, Donation, validateImageSize
from main import constants
from main.utils import generateRandomString

from member.models import Person
from payment.models import MembershipPayment
from parameter.service import getParameterValue


def bondReceiptsDir(instance, filename):
    return path.join(constants.MEDIA_DIR.BOND_RECEIPTS_DIR, f"{uuid4().hex}.{filename.split('.')[-1]}")


class Account(BaseModel):

    account_type: str = models.CharField(
        max_length=1, choices=constants.CHOICES.ACCOUNT_TYPE)
    account_number: str = models.CharField(max_length=25)
    account_holder_name: str = models.CharField(max_length=100)
    bank_name: str = models.CharField(max_length=25)
    account_status: str = models.CharField(
        max_length=1, choices=constants.CHOICES.ACCOUNT_STATUS)
    balance: float = models.DecimalField(max_digits=15, decimal_places=2,
                                         default=0)

    def __str__(self) -> str:
        return "%s - %s" % (self.account_number, self.account_holder_name)

    @property
    def account_type_ar(self) -> str:
        return constants.ACCOUNT_TYPE_AR[int(self.account_type)]

    @property
    def account_status_ar(self) -> str:
        return constants.ACCOUNT_STATUS_AR[int(self.account_status)]


class Bond(BaseModel):

    bond_type: str = models.CharField(
        max_length=1, choices=constants.CHOICES.BOND_TYPE)
    receiving_method: str = models.CharField(
        max_length=1, choices=constants.CHOICES.RECEVING_METHOD)
    reference_number: str = models.CharField(max_length=12, unique=True,
                                             editable=False, null=True)
    receiver_name: str = models.CharField(max_length=100)
    receiver_account_number: str = models.CharField(max_length=25, null=True,
                                                    blank=True)
    sender_name: str = models.CharField(max_length=100)
    sender_account_number: str = models.CharField(max_length=25, null=True,
                                                  blank=True)
    amount: float = models.DecimalField(max_digits=15, decimal_places=2)
    transfer_commission: float = models.DecimalField(max_digits=8,
                                                     decimal_places=2,
                                                     default=0)
    receipt: ImageFieldFile = models.ImageField(upload_to=bondReceiptsDir,
                                                validators=[validateImageSize],
                                                max_length=255)
    status: str = models.CharField(
        max_length=1, choices=constants.CHOICES.BOND_STATUS,
        default=constants.BOND_STATUS.PENDING)
    bond_date: datetime = models.DateField()
    bond_description: str = models.CharField(
        max_length=255, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        self.is_payment_bond = False
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return self.reference_number

    @property
    def bond_type_ar(self) -> str:
        return constants.BOND_TYPE_AR[int(self.bond_type)]

    @property
    def receiving_method_ar(self) -> str:
        return constants.RECEVING_METHOD_AR[int(self.receiving_method)]

    @property
    def status_ar(self) -> str:
        return constants.BOND_STATUS_AR[int(self.status)]

    @property
    def total(self) -> float:
        return self.amount + self.transfer_commission

    @classmethod
    def generateDonationBond(cls, donation: Donation) -> Bond:
        # if account is not exist will throw Account.DoesNotExist error
        account: Account = Account.objects.select_for_update().get(
            account_number=getParameterValue(
                constants.PARAMETERS.DEFAULT_PAYMENT_ACCOUNT))

        bond: Bond = Bond()
        bond.bond_type = constants.BOND_TYPE.INCOMING
        bond.receiving_method = constants.RECEVING_METHOD.TRANSFER
        bond.receiver_name = account.account_holder_name
        bond.receiver_account_number = account.account_number
        bond.sender_name = donation.name
        bond.amount = donation.amount
        bond.transfer_commission = 0
        bond.receipt = donation.receipt
        bond.status = constants.BOND_STATUS.APPROVED
        bond.bond_date = donation.created
        bond.bond_description = f"تبرع رقم {donation.id}"
        account.balance += donation.amount
        bond.save()
        account.save()
        return bond

    @classmethod
    def generatePaymentBond(cls, payment: MembershipPayment) -> Bond:
        # if account is not exist will throw Account.DoesNotExist error
        account: Account = Account.objects.select_for_update().get(
            account_number=getParameterValue(
                constants.PARAMETERS.DEFAULT_PAYMENT_ACCOUNT))

        bond: Bond = Bond()
        bond.is_payment_bond = True
        bond.bond_type = constants.BOND_TYPE.INCOMING
        bond.receiving_method = constants.RECEVING_METHOD.TRANSFER
        bond.reference_number = payment.reference_number
        bond.receiver_name = account.account_holder_name
        bond.receiver_account_number = account.account_number
        bond.sender_name = Person.objects.values(
            'name_ar').get(membership=payment.membership).get("name_ar")
        bond.sender_account_number = payment.membership.card_number
        bond.amount = payment.amount
        bond.transfer_commission = 0
        bond.receipt = payment.receipt
        bond.status = constants.BOND_STATUS.APPROVED
        bond.bond_date = payment.created
        bond.bond_description = f"سداد العضوية رقم \"{payment.membership.card_number}\" لفترة ({payment.period})"
        account.balance += payment.amount
        bond.save()
        account.save()
        return bond

    def save(self, *args, **kwargs) -> None:
        if not self.pk and not self.is_payment_bond:
            self.reference_number = generateRandomString()
        if not self.reference_number:
            raise ValueError("Reference Number Cannot Be Empty")
        return super().save(*args, **kwargs)
