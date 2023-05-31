from __future__ import annotations
import logging
from typing import Optional

from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.core.cache import cache

from . import constants

logger = logging.getLogger(constants.LOGGERS.MODELS)


class BaseModel(models.Model):

    class Meta:
        abstract = True

    id: int = models.AutoField(primary_key=True)
    created: timezone.datetime = models.DateTimeField(auto_now_add=True)
    updated: timezone.datetime = models.DateTimeField(auto_now=True)

    def setCreated(self, created: timezone.datetime) -> None:
        self.created = created
        self.save()

    def setUpdated(self, updated: timezone.datetime) -> None:
        self.updated = updated
        self.save()

    @classmethod
    def create(cls, *args, **kwargs) -> BaseModel:
        return cls.objects.create(*args, **kwargs)

    @classmethod
    def get(cls, *args, **kwargs) -> BaseModel | None:
        """
        This will return None if there are multiple objects returned.
        """
        try:
            obj: BaseModel = cls.objects.get(*args, **kwargs)
            return obj
        except cls.MultipleObjectsReturned:
            return None

    @classmethod
    def getAll(cls) -> QuerySet[BaseModel]:
        """
        Get all objects stored in the database.
        """
        return cls.objects.all()

    @classmethod
    def getAllOrdered(cls, order_by: str, reverse: Optional[bool] = False) -> QuerySet[BaseModel]:
        """
        Get all objects and order them.
        """
        if reverse:
            order_by = '-' + order_by
        return cls.objects.all().order_by(order_by)

    @classmethod
    def getLastInsertedObject(cls, queryset: Optional[QuerySet[BaseModel]] = None) -> BaseModel | None:
        """
        Get the last object from the model or queryset if it was declared.
        """
        query: QuerySet[BaseModel] = queryset
        if queryset is not None:
            if not isinstance(queryset, QuerySet) or not isinstance(queryset.first(), cls):
                raise NotImplementedError
        else:
            query = cls.objects.all()
        try:
            return query.order_by('-id')[0]
        except IndexError:
            return None

    @classmethod
    def filter(cls, *args, **kwargs) -> QuerySet[BaseModel]:
        return cls.objects.filter(*args, **kwargs)

    @classmethod
    def countAll(cls) -> int:
        """
        Count all objects.
        """
        return cls.objects.all().count()

    @classmethod
    def countFiltered(cls, *arg, **kwarg) -> int:
        """
        Count the filtered queryset.
        """
        return cls.objects.filter(*arg, **kwarg).count()

    @classmethod
    def orderFiltered(cls, order_by: str, *args, reverse=False, **kwargs) -> QuerySet[BaseModel]:
        """
        Order the filtered queryset.
        """
        if reverse:
            order_by = '-' + order_by
        return cls.objects.filter(*args, **kwargs).order_by(order_by)

    @classmethod
    def isExists(cls, *arg, **kwarg) -> bool:
        """
        Tre if there is an object in the filtered queryset.
        """
        return cls.objects.filter(*arg, **kwarg).exists()


class Client(BaseModel):

    class Meta:
        abstract = True

    user_agent: str = models.CharField(max_length=256, null=True, blank=True)
    ip: str = models.GenericIPAddressField()

    def setUserAgent(self, user_agent: str) -> None:
        self.user_agent = user_agent
        self.save()

    def setIp(self, ip: str) -> None:
        self.ip = ip
        self.save()


class BlockedClient(Client):

    block_type: str = models.CharField(max_length=1,
                                       choices=constants.CHOICES.BLOCK_TYPE)
    blocked_times: int = models.PositiveSmallIntegerField(default=1)

    @property
    def block_type_ar(self) -> str:
        return constants.BLOCK_TYPES_AR[int(self.block_type)]

    def __str__(self) -> str:
        return f"IP: {self.ip} - User Agent: {self.user_agent}"

    def setBlockType(self, block_type: str) -> None:
        self.block_type = block_type
        self.save()

    def setBlockedTimes(self, blocked_times: int) -> None:
        self.blocked_times = blocked_times
        self.save()


class AuditEntry(Client):

    action: str = models.CharField(
        max_length=1, choices=constants.CHOICES.ACTION)
    username: str = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f'{self.action} - {self.username} - {self.ip}'

    @property
    def action_type(self) -> str:
        return constants.ACTION_STR[int(self.action)].replace('_', ' ').capitalize()

    @property
    def action_type_ar(self) -> str:
        return constants.ACTION_STR_AR[int(self.action)]

    @property
    def isEntry(self) -> str:
        entry: list[str] = constants.ACTION[1:4]
        return True if self.action in entry else False
    
    @classmethod
    def getLastAuditEntry(self) -> QuerySet[AuditEntry]:
        result: QuerySet[AuditEntry] | None = cache.get(
            constants.CACHE.LAST_AUDIT_ENTRY_QUERYSET)
        if not result:
            from parameter.service import getParameterValue
            logger.info("Fetching last audit entry queryset from database.")
            start_chunk_object_id: int = getParameterValue(
                constants.PARAMETERS.MAGIC_NUMBER)
            result = AuditEntry.filter(
                id__gte=start_chunk_object_id)
            cache.set(constants.CACHE.LAST_AUDIT_ENTRY_QUERYSET, result, 
                      constants.DEFAULT_CACHE_EXPIRE)
        
        return result

    def setAction(self, action: str) -> None:
        self.action = action
        self.save()

    def setUsername(self, username: str) -> None:
        self.username = username
        self.save()

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        last_audit_entry: QuerySet[AuditEntry] = self.getLastAuditEntry()
        if last_audit_entry is not None:
            last_audit_entry = last_audit_entry | AuditEntry.objects.filter(pk=self.pk)
            cache.set(constants.CACHE.LAST_AUDIT_ENTRY_QUERYSET, last_audit_entry, constants.DEFAULT_CACHE_EXPIRE)
