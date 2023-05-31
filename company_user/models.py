from typing import Set

from django.contrib.auth.models import Group, User
from django.core.cache import cache
from django.db import models

from main import constants
from main.models import BaseModel


class Role(BaseModel):
    name: str = models.CharField(max_length=100)
    groups: Set[Group] = models.ManyToManyField(Group)
    description = models.TextField()

    @property
    def permissions(self) -> Set[str]:
        permissions: Set[str] = cache.get(f'ROLE_{self.id}')
        if not permissions:
            permissions = set()
            groups: Set[str] = self.groups.all().values_list('name', flat=True)
            for group in groups:
                for permission in constants.STAFF_PERMISSIONS[group]:
                    permissions.add(permission)

            cache.set(f'ROLE_{self.id}', permissions,
                      constants.DEFAULT_CACHE_EXPIRE)

        return permissions

    def getArStrPermissions(self) -> str:
        permissions: Set[str] = set()
        groups: Set[str] = self.groups.all().values_list('name', flat=True)
        for group in groups:
            permissions.add(constants.GROUPS_AR[group])

        return " - ".join(permissions)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        cache.delete(f'ROLE_{self.id}')


class CompanyUser(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)

    def __str__(self):
        return self.user.username
