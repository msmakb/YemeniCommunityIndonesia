from uuid import uuid4
from PIL import Image

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.utils.timezone import datetime

from main import constants
from main.image_processing import ImageProcessingError, ImageProcessor
from main.models import BaseModel


def photographsDir(instance, filename):
    return settings.MEDIA_ROOT / constants.MEDIA_DIR.PHOTOGRAPHS_DIR / f"{uuid4().hex}.{filename.split('.')[-1]}"


def passportDir(instance, filename):
    return settings.MEDIA_ROOT / constants.MEDIA_DIR.PASSPORTS_DIR / f"{uuid4().hex}.{filename.split('.')[-1]}"


def residencyImagesDir(instance, filename):
    return settings.MEDIA_ROOT / constants.MEDIA_DIR.RESIDENCY_IMAGES_DIR / f"{uuid4().hex}.{filename.split('.')[-1]}"


def membershipImagesDir(instance, filename):
    return settings.MEDIA_ROOT / constants.MEDIA_DIR.MEMBERSHIP_IMAGES_DIR / f"{uuid4().hex}.{filename.split('.')[-1]}"


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
    membership_card: Image = models.ImageField(
        upload_to=membershipImagesDir, max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return self.card_number

    @property
    def getMembershipType(self):
        return constants.MEMBERSHIP_TYPE_AR[int(self.membership_type)]

    @property
    def getMembershipTypeEnglish(self):
        return constants.MEMBERSHIP_TYPE_EN[int(self.membership_type)]


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
    photograph: Image = models.ImageField(
        upload_to=photographsDir, max_length=255, null=True, blank=True)
    passport_photo: Image = models.ImageField(
        upload_to=passportDir, max_length=255)
    residency_photo: Image = models.ImageField(
        upload_to=residencyImagesDir, max_length=255)
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

    def clean(self) -> None:
        if not self.photograph:
            if self.gender == constants.GENDER.MALE:
                raise ValidationError("هذا الحقل مطلوب")
            else:
                image_io: bytes = ImageProcessor.validateAndResizePhotograph(
                    settings.MEDIA_ROOT / constants.MEDIA_DIR.PHOTOGRAPHS_DIR / "female_no_image.jpg")
                self.photograph = ContentFile(image_io, "no_image.jpg")
        else:
            try:
                image_io: bytes = ImageProcessor.validateAndResizePhotograph(
                    self.photograph)
                self.photograph = ContentFile(image_io, self.photograph.name)
            except ImageProcessingError as error:
                raise ValidationError(str(error))

        return super().clean()
