from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CompanyUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'company_user'

    def ready(self) -> None:
        from . import signals

        post_migrate.connect(
            signals.createRoleForSuperuser, sender=self)

        return super().ready()
