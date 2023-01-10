from django.apps import AppConfig
from django.db.models.signals import pre_delete


class MemberConfig(AppConfig):
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'member'

    def ready(self) -> None:
        from . import signals
        from member.models import Person

        pre_delete.connect(signals.cleanUpPersonData, sender=Person)

        return super().ready()
