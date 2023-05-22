from django.apps import AppConfig
from django.contrib.auth.signals import (user_logged_in, user_logged_out,
                                         user_login_failed)
from django.db.models.signals import post_migrate


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self) -> None:
        from . import signals

        user_logged_in.connect(signals.userLoggedIn)
        user_logged_out.connect(signals.userLoggedOut)
        user_login_failed.connect(signals.userLoggedFailed)

        post_migrate.connect(signals.createGroups, sender=self)

        return super().ready()
