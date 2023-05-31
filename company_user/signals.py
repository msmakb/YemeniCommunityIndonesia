from .models import Role


def createRoleForSuperuser(**kwargs) -> None:
    if Role.getAll().exists():
        pass

    Role.create(
        name='superuser',
        description='Superuser',
    )
