import ast
import re
import traceback
from logging import Logger, getLogger
from os import path
from threading import Thread
from typing import Final, List, Optional, Tuple
from uuid import uuid4

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.mail import EmailMessage
# from django.core.mail import send_mass_mail
from django.conf import settings
from django.core.validators import validate_email
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone

from main import constants
from main.models import BaseModel
from member.models import Person
from parameter.service import getParameterValue


logger: Logger = getLogger(constants.LOGGERS.BROADCAST)


class InvalidIdentifierError(Exception):
    pass


def emailAttachmentsDir(instance, filename):
    return path.join(constants.MEDIA_DIR.EMAIL_ATTACHMENTS_DIR, f"{uuid4().hex}.{filename.split('.')[-1]}")


class Broadcast(BaseModel):

    class Meta:
        abstract = True

    subject: str = models.CharField(max_length=50)
    body: str = models.TextField()
    broadcast_date: str = models.DateTimeField(
        null=True, blank=True, editable=False)
    is_broadcasting: bool = models.BooleanField(default=False, editable=False)
    is_broadcasted: bool = models.BooleanField(default=False, editable=False)


class EmailBroadcast(Broadcast):

    email_list: str = models.TextField()
    has_attachment: bool = models.BooleanField(default=False, editable=False)
    is_special_email_broadcast: bool = models.BooleanField(default=False)
    attache_membership_card: bool = models.BooleanField(default=False)

    @property
    def recipientsCount(self) -> int:
        return len(self.getRecipientsAsList())

    def getRecipientsAsList(self) -> list[str]:
        return ast.literal_eval(self.email_list)

    def _broadcast(self) -> None:
        logger.info("===== Start Broadcasting Email =====")
        email: EmailMessage = EmailMessage(
            subject=self.subject,
            body=self.body,
            from_email=settings.EMAIL_HOST_USER,
            to=[getParameterValue(constants.PARAMETERS.PLACEHOLDER_EMAIL)],
            bcc=self.getRecipientsAsList()
        )
        email.fail_silently = False
        if self.has_attachment:
            attachments: QuerySet[Attachment] = Attachment.filter(
                email_broadcast=self,
            )
            for attachment in attachments:
                email.attach(
                    attachment.file_name,
                    attachment.content.file.read(),
                    attachment.mimetype
                )
        try:
            email.send()
            self.is_broadcasted = True
            self.broadcast_date = timezone.now()
        except Exception as e:
            logger.error("Failed to broadcast. Email subject: " + self.subject)

        self.is_broadcasting = False
        self.save()
        logger.info("===== Finish Broadcasting Email =====")

    def _special_broadcast(self, is_test_email: Optional[bool] = False,
                           test_email: Optional[bool] = None) -> None:
        if not self.is_special_email_broadcast:
            raise ValueError("This email is not a special email broadcast")

        logger.info("===== Start Broadcasting Special Email =====")

        ALLOWED_VARIABLES: Final[Tuple[str, ...]] = (
            'id', 'name_ar', 'name_en', 'date_of_birth',
            'call_number', 'whatsapp_number', 'email',
            'address__street_address', 'address__district',
            'address__city', 'address__province', 'address__postal_code',
            'membership__card_number', 'membership__membership_type',
            'membership__issue_date', 'membership__expire_date'
        )

        requested_fields: list[str] = []
        body_variables: list[str] = re.findall(r"\{(.*?)\}", self.body)
        for var in body_variables:
            if var in ALLOWED_VARIABLES:
                requested_fields.append(var)
            else:
                raise InvalidIdentifierError(
                    "معرف متغير غير صالح " + '{' + var + '}')

        if 'email' not in requested_fields:
            requested_fields.append('email')

        if self.attache_membership_card:
            requested_fields.append('membership__membership_card')
            requested_fields.append('membership__card_number')

        email_list = self.getRecipientsAsList()
        if test_email is not None:
            email_list = [test_email]

        data = Person.objects.prefetch_related(
            'address', 'membership'
        ).values(*requested_fields).filter(
            email__in=email_list
        ).iterator(chunk_size=100)

        no_data = True
        for person in data:
            no_data = False

            email: EmailMessage = EmailMessage(
                subject=self.subject,
                body=self.body.format(**person),
                from_email=settings.EMAIL_HOST_USER,
                to=[person['email']],
            )
            if self.has_attachment:
                attachments: QuerySet[Attachment] = Attachment.filter(
                    email_broadcast=self,
                )
                for attachment in attachments:
                    email.attach(
                        attachment.file_name,
                        attachment.content.file.read(),
                        attachment.mimetype
                    )

            try:
                if self.attache_membership_card and person['membership__membership_card']:
                    with open(str(settings.MEDIA_ROOT / person[
                            'membership__membership_card']), 'rb') as file:
                        email.attach(
                            person['membership__card_number'] + '.jpg',
                            file.read(),
                            constants.MIME_TYPE.JPEG
                        )
            except Exception as e:
                logger.error(
                    "Failed to attache the membership card to the person id: " + person.get('id'))
                logger.error(traceback.format_exc())

            try:
                logger.info("sending to " + person['email'])
                email.send()
            except Exception as e:
                logger.error(
                    "Failed to broadcast. Email subject: " + self.subject)

        if no_data:
            raise ValueError(
                "لم يتم العثور على سجلات مع قائمة البريد الإلكتروني هذه")

        self.is_broadcasted = True
        self.broadcast_date = timezone.now()
        self.is_broadcasting = False
        if not is_test_email:
            self.save()

        cache.delete("BROADCASTING_SUCCESS_COUNT_" + str(self.id))
        cache.delete("BROADCASTING_FAILED_COUNT_" + str(self.id))
        logger.info("===== Finish Broadcasting Special Email =====")

    def broadcast(self) -> None:
        if self.is_broadcasting:
            raise ValidationError("The Email is already broadcasting")

        self.is_broadcasting = True
        self.save()

        thread: Thread = Thread(target=self._broadcast)
        thread.start()

    def testBroadcast(self, test_email: str):
        validate_email(test_email)
        email: EmailMessage = EmailMessage(
            self.subject,
            self.body,
            settings.EMAIL_HOST_USER,
            [test_email]
        )
        email.fail_silently = False
        if self.has_attachment:
            attachments: QuerySet[Attachment] = Attachment.filter(
                email_broadcast=self,
            )
            for attachment in attachments:
                email.attach(
                    attachment.file_name,
                    attachment.content.file.read(),
                    attachment.mimetype
                )

        email.send()

    def specialBroadcast(self) -> None:
        if self.is_broadcasting:
            raise ValidationError("The Email is already broadcasting")

        EmailBroadcast.objects.filter(id=self.id).update(is_broadcasting=True)

        thread: Thread = Thread(target=self._special_broadcast)
        thread.start()

    def testSpecialBroadcast(self, test_email: str) -> None:
        self._special_broadcast(True, test_email)


class Attachment(BaseModel):

    class Meta:
        ordering = ['-created']

    email_broadcast: EmailBroadcast = models.ForeignKey(
        EmailBroadcast, on_delete=models.CASCADE)
    file_name: str = models.CharField(max_length=50)
    content = models.FileField(upload_to=emailAttachmentsDir, max_length=255)
    mimetype: str = models.CharField(
        max_length=100, choices=constants.CHOICES.MIME_TYPE)

    @property
    def file_extension(self) -> str:
        try:
            file: TemporaryUploadedFile = self.content.file
            return file.name.rsplit('.', maxsplit=1)[-1]
        except FileNotFoundError:
            return ""

    def clean(self) -> None:

        MimetypeError: ValidationError = ValidationError(
            "الملف الذي تم رفعه لا يتطابق مع نوع الملف المحدد"
        )
        match self.mimetype:
            case constants.MIME_TYPE.AVI:
                if self.file_extension != 'avi':
                    raise MimetypeError
            case constants.MIME_TYPE.JPEG:
                if self.file_extension != 'jpg' and self.file_extension != 'jpeg':
                    raise MimetypeError
            case constants.MIME_TYPE.MP4:
                if self.file_extension != 'mp4':
                    raise MimetypeError
            case constants.MIME_TYPE.MP3:
                if self.file_extension != 'mp3':
                    raise MimetypeError
            case constants.MIME_TYPE.PNG:
                if self.file_extension != 'png':
                    raise MimetypeError
            case constants.MIME_TYPE.PDF:
                if self.file_extension != 'pdf':
                    raise MimetypeError
            case constants.MIME_TYPE.RAR:
                if self.file_extension != 'rar':
                    raise MimetypeError
            case constants.MIME_TYPE.TEXT:
                if self.file_extension != 'txt':
                    raise MimetypeError
            case constants.MIME_TYPE.WAV:
                if self.file_extension != 'wav':
                    raise MimetypeError
            case constants.MIME_TYPE.MS_EXCEL:
                if self.file_extension != 'xls':
                    raise MimetypeError
            case constants.MIME_TYPE.MS_POWERPOINT:
                if self.file_extension != 'ppt':
                    raise MimetypeError
            case constants.MIME_TYPE.MS_EXCEL_OPEN_XML:
                if self.file_extension != 'xlsx':
                    raise MimetypeError
            case constants.MIME_TYPE.MS_POWERPOINT_OPEN_XML:
                if self.file_extension != 'pptx':
                    raise MimetypeError

        return super().clean()

    def save(self, *args, **kwargs) -> None:
        file: TemporaryUploadedFile = self.content.file
        if not '.' in self.file_name[-5:]:
            self.file_name += f".{self.file_extension}"

        return super().save(*args, **kwargs)
