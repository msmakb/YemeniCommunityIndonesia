from typing import Set

from django.contrib.auth.models import Group, User
from django.core.cache import cache
from django.db import models
from django.db.models.query import QuerySet

from main import constants
from main.models import BaseModel


class Role(BaseModel):
    name: str = models.CharField(max_length=100, unique=True)
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
        groups: QuerySet[Group] = self.groups.all()
        for group in groups:
            permissions.add(constants.GROUPS_AR[group.name])

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

    @classmethod
    def getCompanyUserByUserObject(cls, user: User):
        CACHED_COMPANY_USER_KEY = "COMPANY_USER:" + str(User.id)
        if cache.get(CACHED_COMPANY_USER_KEY):
            return cache.get(CACHED_COMPANY_USER_KEY)

        company_user: CompanyUser = CompanyUser.objects.select_related(
            'user', 'role').prefetch_related(
            'role__groups').get(
            user=user)
        cache.set(CACHED_COMPANY_USER_KEY, company_user, 300)
        return company_user
