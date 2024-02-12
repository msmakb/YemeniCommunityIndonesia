from os import path
from uuid import uuid4

from django.db import models
from django.db.models.fields.files import ImageFieldFile
from django.utils.timezone import datetime

from main.models import BaseModel, validateImageSize
from main import constants
from main.utils import generateRandomString


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
                                                     decimal_places=2)
    receipt: ImageFieldFile = models.ImageField(upload_to=bondReceiptsDir,
                                                validators=[validateImageSize],
                                                max_length=255)
    status: str = models.CharField(
        max_length=1, choices=constants.CHOICES.BOND_STATUS)
    bond_date: datetime = models.DateField()
    bond_description: str = models.CharField(max_length=255, null=True, blank=True)

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

    def save(self, *args, **kwargs) -> None:
        if not self.pk:
            self.reference_number = generateRandomString()
        return super().save(*args, **kwargs)
