from logging import Logger, getLogger
from uuid import uuid4
from os import path

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import EmailMessage
from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone

from main import constants
from main.models import BaseModel


logger: Logger = getLogger(constants.LOGGERS.BROADCAST)

def emailAttachmentsDir(instance, filename):
    return path.join(constants.MEDIA_DIR.EMAIL_ATTACHMENTS_DIR, f"{uuid4().hex}.{filename.split('.')[-1]}")

class Broadcast(BaseModel):

    class Meta:
        abstract = True

    subject: str = models.CharField(max_length=50)
    body: str = models.TextField()
    broadcast_date: str = models.DateTimeField(null=True, blank=True)
    is_broadcasting: bool = models.BooleanField(default=False)
    is_broadcasted: bool = models.BooleanField(default=False)

class EmailBroadcast(Broadcast):

    email_list: str = models.TextField()
    has_attachment: bool = models.BooleanField(default=False)

    @property
    def recipientsCount(self) -> int:
        return len(self.getRecipientsAsList())

    def getRecipientsAsList(self) -> list[str]:
        import ast
        return ast.literal_eval(self.email_list)

    def _broadcast(self) -> None:
        logger.info("===== Start Broadcasting Email =====")
        email: EmailMessage = EmailMessage(
            self.subject,
            self.body,
            settings.EMAIL_HOST_USER,
            self.getRecipientsAsList()
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

    
    def broadcast(self) -> None:
        if self.is_broadcasting:
            raise ValidationError("The Email is already broadcasting")
        
        self.is_broadcasting = True
        self.save()

        from threading import Thread
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

from django.core.files.uploadedfile import TemporaryUploadedFile

class Attachment(BaseModel):

    class Meta:
        ordering = ['-created']

    email_broadcast: EmailBroadcast = models.ForeignKey(
        EmailBroadcast, on_delete=models.CASCADE)
    file_name: str = models.CharField(max_length=50)
    content = models.FileField(upload_to=emailAttachmentsDir, max_length=255)
    mimetype: str = models.CharField(max_length=100, choices=constants.CHOICES.MIME_TYPE)

    @property
    def file_extension(self) -> str:
        file: TemporaryUploadedFile = self.content.file
        return file.name.rsplit('.', maxsplit=1)[-1]

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
