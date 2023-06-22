from os import path
from uuid import uuid4

from django.db import models
from django.db.models.fields.files import ImageFieldFile

from main import constants
from main.models import BaseModel
from main.utils import generateRandomString
from member.models import Membership, validateImageSize


def membershipPaymentReceiptsDir(instance, filename):
    return path.join(constants.MEDIA_DIR.MEMBERSHIP_PAYMENT_RECEIPTS_DIR, f"{uuid4().hex}.{filename.split('.')[-1]}")


class MembershipPayment(BaseModel):

    membership: Membership = models.ForeignKey(Membership, on_delete=models.CASCADE,
                                               related_name='payments', related_query_name='payment')
    reference_number: str = models.CharField(max_length=12, unique=True,
                                             editable=False, null=True)
    receipt: ImageFieldFile = models.ImageField(upload_to=membershipPaymentReceiptsDir,
                                                validators=[validateImageSize], max_length=255)
    amount: float = models.DecimalField(max_digits=8, decimal_places=2)
    number_of_months: int = models.PositiveSmallIntegerField()
    from_month: str = models.CharField(max_length=7)
    status: str = models.CharField(max_length=1, choices=constants.CHOICES.PAYMENT_STATUS,
                                   default=constants.PAYMENT_STATUS.PENDING)
    note: str = models.CharField(max_length=100, null=True, blank=True)

    @property
    def period(self) -> str:
        if self.number_of_months == 1:
            return constants.MONTHS_AR[int(self.from_month[:2]) - 1] + ' ' + self.from_month[3:]

        to_month: str = self.from_month
        months = self.number_of_months - 1
        while months != 0:
            months -= 1
            if to_month[:2] == '12':
                to_month = f'01/{int(to_month[3:])+1}'
            else:
                to_month = f'{str(int(to_month[:2])+1).rjust(2, "0")}{to_month[2:]}'

        result: str = ''
        result += constants.MONTHS_AR[int(self.from_month[:2]) - 1]
        result += ' '
        result += self.from_month[3:]
        result += ' - '
        result += constants.MONTHS_AR[int(to_month[:2]) - 1]
        result += ' '
        result += to_month[3:]
        return result

    @property
    def status_ar(self) -> str:
        return constants.PAYMENT_STATUS_AR[int(self.status)]

    def updateMembershipLastMonthPaid(self) -> None:
        if self.status != constants.PAYMENT_STATUS.APPROVED:
            return

        last_month_paid: str = self.from_month
        if self.number_of_months != 1:
            months = self.number_of_months - 1
            while months != 0:
                months -= 1
                if last_month_paid[:2] == '12':
                    last_month_paid = f'01/{int(last_month_paid[3:])+1}'
                else:
                    last_month_paid = f'{str(int(last_month_paid[:2])+1).rjust(2, "0")}{last_month_paid[2:]}'

        Membership.objects.filter(pk=self.membership.id).update(
            last_month_paid=last_month_paid
        )

    def save(self, *args, **kwargs) -> None:
        if not self.pk:
            self.reference_number = generateRandomString()
        return super().save(*args, **kwargs)
