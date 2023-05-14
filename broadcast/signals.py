import os

from .models import Attachment


def deleteAttachmentFile(sender: Attachment, instance: Attachment, *args, **kwargs):
    if instance.content and os.path.isfile(instance.content.path):
        os.remove(instance.content.path)
