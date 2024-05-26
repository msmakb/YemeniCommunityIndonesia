from __future__ import annotations
from io import BytesIO
from os import path
from typing import Any
from uuid import uuid4

from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.db import models
from django.db.models import Case, When
from django.db.models.fields.files import ImageFieldFile
from django.utils.timezone import datetime

from PIL import Image as Img
from PIL.Image import Image

from main import constants
from main.image_processing import ImageProcessingError, ImageProcessor
from main.models import BaseModel
from parameter.service import getParameterValue


def photographsDir(instance, filename):
    return path.join(constants.MEDIA_DIR.PHOTOGRAPHS_DIR, f"{uuid4().hex}.{filename.split('.')[-1]}")


def passportDir(instance, filename):
    return path.join(constants.MEDIA_DIR.PASSPORTS_DIR, f"{uuid4().hex}.{filename.split('.')[-1]}")


def residencyImagesDir(instance, filename):
    return path.join(constants.MEDIA_DIR.RESIDENCY_IMAGES_DIR, f"{uuid4().hex}.{filename.split('.')[-1]}")


def membershipImagesDir(instance, filename):
    return path.join(constants.MEDIA_DIR.MEMBERSHIP_IMAGES_DIR, f"{uuid4().hex}.{filename.split('.')[-1]}")


def validateImageSize(image: ImageFieldFile):
    try:
        file: TemporaryUploadedFile = image.file
        file_size: int = file.size
        max_size: int = getParameterValue(constants.PARAMETERS.IMAGE_MAX_SIZE)
        if file_size > 1_048_576 * max_size:
            raise ValidationError(
                f"حجم الصورة كبير جدا، يجب ألا يتجاوز حجم الصورة {max_size} ميقا بايت")
    except FileNotFoundError:
        # Do noting (This case will not happened by the user, the file is required)
        pass


class Academic(BaseModel):
    academic_qualification: str = models.CharField(
        max_length=1, choices=constants.CHOICES.ACADEMIC_QUALIFICATION)
    school: str = models.CharField(max_length=50, null=True, blank=True)
    major: str = models.CharField(max_length=50, null=True, blank=True)
    semester: int = models.PositiveSmallIntegerField(null=True, blank=True)

    @property
    def getAcademicQualification(self) -> str:
        return constants.ACADEMIC_QUALIFICATION_AR[int(self.academic_qualification)]


class Address(BaseModel):
    street_address: str = models.CharField(max_length=50)
    district: str = models.CharField(max_length=20)
    city: str = models.CharField(
        max_length=20, choices=constants.CHOICES.CITIES)
    province: str = models.CharField(max_length=20)
    postal_code: str = models.CharField(max_length=10, null=True, blank=True)

    @property
    def getCityAr(self):
        return constants.CITIES.get(self.city)


class Membership(BaseModel):
    card_number: str = models.CharField(max_length=10, unique=True)
    membership_type: str = models.CharField(
        max_length=1, choices=constants.CHOICES.MEMBERSHIP_TYPE)
    issue_date: datetime = models.DateField(auto_now_add=True)
    expire_date: datetime = models.DateField()
    membership_card: ImageFieldFile = models.ImageField(
        upload_to=membershipImagesDir, max_length=255, null=True, blank=True)
    last_month_paid: str = models.CharField(max_length=7, blank=True,
                                            null=True)

    def __str__(self) -> str:
        return self.card_number

    @property
    def getMembershipType(self):
        return constants.MEMBERSHIP_TYPE_AR[int(self.membership_type)]

    @property
    def getMembershipTypeEnglish(self):
        return constants.MEMBERSHIP_TYPE_EN[int(self.membership_type)]

    def hasPendingPayment(self) -> bool:
        return self.payments.filter(status=constants.PAYMENT_STATUS.PENDING).exists()

    def getNextPaymentStartMonth(self) -> str:
        last_month_paid: str = self.last_month_paid
        if last_month_paid is None:
            last_month_paid = datetime.strftime(
                self.issue_date, '%m/%Y')

        if last_month_paid[:2] == '12':
            from_month: datetime = datetime.strptime(
                f'01/{int(last_month_paid[3:])+1}', '%m/%Y')
        else:
            from_month: datetime = datetime.strptime(
                f'{int(last_month_paid[:2])+1}{last_month_paid[2:]}', '%m/%Y')

        return datetime.strftime(from_month, '%m/%Y')


class FamilyMembers(BaseModel):
    family_name: str = models.CharField(max_length=15)
    member_count: int = models.PositiveSmallIntegerField()


class FamilyMembersChild(BaseModel):
    family_members: FamilyMembers = models.ForeignKey(
        FamilyMembers, on_delete=models.CASCADE)
    name: str = models.CharField(max_length=50, null=True, blank=True)
    age: int = models.PositiveSmallIntegerField(null=True, blank=True)


class FamilyMembersWife(BaseModel):
    family_members: FamilyMembers = models.ForeignKey(
        FamilyMembers, on_delete=models.CASCADE)
    name: str = models.CharField(max_length=50, null=True, blank=True)
    age: int = models.PositiveSmallIntegerField(null=True, blank=True)


class Person(BaseModel):
    name_ar: str = models.CharField(max_length=50)
    name_en: str = models.CharField(max_length=50)
    gender: str = models.CharField(
        max_length=1, choices=constants.CHOICES.GENDER)
    place_of_birth: str = models.CharField(max_length=20)
    date_of_birth: datetime = models.DateField()
    call_number: str = models.CharField(max_length=20)
    whatsapp_number: str = models.CharField(max_length=20)
    email: str = models.EmailField(max_length=254)
    job_title: str = models.CharField(
        max_length=20, choices=constants.CHOICES.JOB_TITLE)
    period_of_residence: str = models.CharField(
        max_length=1, choices=constants.CHOICES.PERIOD_OF_RESIDENCE)
    photograph: ImageFieldFile = models.ImageField(
        upload_to=photographsDir, validators=[validateImageSize],
        max_length=255, null=True, blank=True)
    passport_photo: ImageFieldFile = models.ImageField(
        upload_to=passportDir, validators=[validateImageSize],
        max_length=255)
    residency_photo: ImageFieldFile = models.ImageField(
        upload_to=residencyImagesDir, validators=[validateImageSize],
        max_length=255)
    academic: Academic = models.ForeignKey(
        Academic, on_delete=models.SET_NULL, null=True, blank=True)
    address: Address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, blank=True)
    membership: Membership = models.ForeignKey(
        Membership, on_delete=models.SET_NULL, null=True, blank=True)
    family_members: FamilyMembers = models.ForeignKey(
        FamilyMembers, on_delete=models.SET_NULL, null=True, blank=True)
    account: User = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    passport_number: str = models.CharField(
        max_length=15, null=True, blank=True)
    is_validated: bool = models.BooleanField(default=False)
    is_request_membership: bool = models.BooleanField(default=False)

    @property
    def getGender(self) -> str:
        return constants.GENDER_AR[int(self.gender)]

    @property
    def getJobTitle(self):
        return constants.JOB_TITLE_AR[int(self.job_title)]

    @property
    def periodOfResidence(self) -> str:
        return constants.PERIOD_OF_RESIDENCE_AR[int(self.period_of_residence)]

    @classmethod
    def getUserData(cls, user: User) -> dict[str, Any]:
        user_data: dict[str, Any] = cache.get('USER_DATA_' + str(user.id))
        changed: bool = True
        person: Person | None = None

        if not user_data:
            person = Person.objects.select_related(
                "membership").get(account=user)
            user_data = {}
            changed = True

        if not user_data.get('has_membership'):
            changed = True
            user_data['has_membership'] = Person.objects.annotate(
                has_membership=Case(
                    When(membership__isnull=False, then=True),
                    default=False,
                    output_field=models.BooleanField())
            ).filter(account=user).values_list(
                'has_membership', flat=True).get()

        if user_data.get('has_membership') and not user_data.get('membership_id'):
            changed = True
            if person and person.membership:
                user_data['membership_id'] = person.membership.id
                user_data['membership_card_number'] = person.membership.card_number
            else:
                user_data['membership_id'] = Person.filter(
                    account=user).values_list('membership', flat=True).get()
                user_data['membership_card_number'] = Person.filter(
                    account=user).values('membership__card_number', flat=True).get()

        if not user_data.get('name_ar'):
            changed = True
            if person:
                user_data['name_ar'] = person.name_ar
            else:
                user_data['name_ar'] = Person.filter(
                    account=user).values_list('name_ar', flat=True).get()

        if not user_data.get('email'):
            changed = True
            if person:
                user_data['email'] = person.email
            else:
                user_data['email'] = Person.filter(
                    account=user).values_list('email', flat=True).get()

        if changed:
            cache.set('USER_DATA_' + str(user.id), user_data, None)

        return user_data

    def clean(self) -> None:
        if self.pk and self.__class__.get(pk=self.pk).photograph.name == self.photograph.name:
            return super().clean()
        if not self.photograph:
            if self.gender == constants.GENDER.MALE:
                raise ValidationError("هذا الحقل مطلوب")
            else:
                image_path: str = settings.MEDIA_ROOT / "templates/female_no_image.jpg"
                image: Image = Img.open(image_path)
                image_io: BytesIO = BytesIO()
                image = image.convert('RGB')
                image.save(image_io, format="JPEG", quality=85)
                image.close()
                self.photograph = ContentFile(
                    image_io.getvalue(), "no_image.jpg")
        else:
            try:
                image_io: bytes = ImageProcessor.validateAndResizePhotograph(
                    self.photograph)
                self.photograph = ContentFile(image_io, self.photograph.name)
            except ImageProcessingError as error:
                raise ValidationError(str(error))
            except IOError:
                raise ValidationError("صورة غير صالحة")

        return super().clean()
