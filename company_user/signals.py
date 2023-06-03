from .models import Role


def createRoleForSuperuser(**kwargs) -> None:
    if not Role.filter(name='superuser').exists():
        Role.create(
            name='superuser',
            description='Superuser',
        )
