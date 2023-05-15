from django.apps import AppConfig
from django.db.models.signals import pre_delete


class BroadcastConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'broadcast'


    def ready(self) -> None:
        from . import signals
        from .models import Attachment

        pre_delete.connect(signals.deleteAttachmentFile, sender=Attachment)

        return super().ready()