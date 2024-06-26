from django.apps import AppConfig

from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ParameterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'parameter'

    def ready(self) -> None:
        from . import signals

        post_migrate.connect(signals.createParameters, sender=self)

        return super().ready()